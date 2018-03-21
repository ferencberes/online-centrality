import math
import operator
import pandas as pd
from scipy.stats import pearsonr,spearmanr,kendalltau,rankdata
import itertools
import numpy as np


### Basic correlation measures ###

def corr_pearson(top_list_prev, top_list, k=None):
    """Compute Pearson correlation (based on Scipy)
    NOTE: Lists are DataFrame columns AND they must be sorted according to their value!!!"""
    if k != None:
        top_list_prev = get_top_k(top_list_prev, k)
        top_list = get_top_k(top_list, k)
    list_a, list_b = proc_corr(top_list_prev, top_list)
    return [pearsonr(list_a, list_b)[0]]

def corr_spearman(top_list_prev, top_list, k=None):
    """Compute Spearman's Rho correlation (based on Scipy)
    NOTE: Lists are DataFrame columns AND they must be sorted according to their value!!!"""
    if k != None:
        top_list_prev = get_top_k(top_list_prev, k)
        top_list = get_top_k(top_list, k)
    list_a, list_b = proc_corr(top_list_prev, top_list)
    return [spearmanr(list_a, list_b)[0]]

def corr_kendalltau(top_list_prev, top_list, k=None):
    """Compute Kendall's Tau correlation (based on Scipy).
    NOTE: Lists are DataFrame columns AND they must be sorted according to their value!!!"""
    # it is irrelevant whether we compute kendall for ranks or scores.
    if k != None:
        top_list_prev = get_top_k(top_list_prev, k)
        top_list = get_top_k(top_list, k)
    list_a, list_b = proc_corr(top_list_prev, top_list)
    return [kendalltau(list_a, list_b)[0]]

def corr_weighted_kendalltau(top_list_prev, top_list, use_fast=True):
    """Compute weighted Kendall's Tau correlation (based on custom implementation!).
    NOTE: Lists are DataFrame columns AND they must be sorted according to their value!!!"""
    # it is irrelevant whether we compute kendall for ranks or scores.
    list_a, list_b = proc_corr(top_list_prev, top_list)
    if len(list_a) != len(list_b):
        raise RuntimeError("The length of 'list_a' and 'list_b' must be the same!")
    if use_fast:
        return [fast_weighted_kendall(list_a, list_b)[1]]
    else:
        rank_list_a = tiedrank(list_a)
        rank_list_b = tiedrank(list_b)
        return [computeWKendall(rank_list_a,rank_list_b,ranked_input=True)[1]]

### Score list preprocessor functions ###

def get_top_k(l,k):
    """Get k biggest score from a list"""
    if k==None:
        return l
    else:
        return l.sort_values("score",ascending=False).head(k)

def proc_corr(l_1, l_2):
    """Fill lists with scores ordered by the ranks in the second list. 
    NOTE: Lists are DataFrame columns AND they must be sorted according to their value!!!"""
    l1=l_1.copy()
    l2=l_2.copy()
    l1.columns=['l1_col']
    l2.columns=['l2_col']
    df=pd.concat([l2, l1], axis=1).fillna(0.0)
    index_diff=list(set(list(l1.index))-set(list(l2.index)))
    index_diff.sort()
    sorted_id=list(l2.index)+index_diff # NOTE: input lists must be sorted! For custom weighted correlations?
    df=df.reindex(sorted_id)
    return np.array(df['l1_col']), np.array(df['l2_col'])


def tiedrank(vector):
    """Return rank with average tie resolution. Rank is based on decreasing score order"""
    return (len(vector) + 1) * np.ones(len(vector)) - rankdata(vector, method='average')


def get_union_of_active_nodes(day_1, day_2):
    """Find common subvectors of non-zero elements. (we only consider positive scores to be active nodes)"""
    ind_one=np.nonzero(day_1)[0];
    ind_two=np.nonzero(day_2)[0];
    ind=np.union1d(ind_one,ind_two)
    ranks_day_one=tiedrank(day_1[ind])
    ranks_day_two=tiedrank(day_2[ind])
    return ranks_day_one, ranks_day_two


def computeWKendall(day_1,day_2,ranked_input=False):
    """Compute Kendall and WKendall only for active (nonzero) positions."""
    if ranked_input:
        rankX, rankY = day_1, day_2
    else:
        rankX, rankY = get_union_of_active_nodes(day_1, day_2)
    n = len(rankX)
    denomX, denomY = 0, 0
    denomXW, denomYW = 0, 0
    num, numW = 0, 0 

    for i in range(n):
        for j in range(i+1,n):
            weightXY= 1.0/rankY[i]+1.0/rankY[j]
            weightX=1.0/rankX[i]+1.0/rankX[j];
            weightY=1.0/rankY[i]+1.0/rankY[j];
            termX=np.sign(rankX[i]-rankX[j]);
            termY=np.sign(rankY[i]-rankY[j]);
            denomX=denomX+(termX)**2;
            denomY=denomY+(termY)**2;
            denomXW=denomXW+(termX)**2*weightX;
            denomYW=denomYW+(termY)**2*weightY;
            num=num+termX*termY;
            numW=numW+termX*termY*weightXY;

    Kendall=num/math.sqrt(denomX*denomY);
    WKendall=numW/math.sqrt(denomXW*denomYW);
    return [Kendall, WKendall]


### FastWKEndall ###

def count_ties(list_with_ties):
    same_as_next = [list_with_ties[i]==list_with_ties[i+1] for i in range(len(list_with_ties)-1)]+[False]
    count = 1
    tie_counts = []
    for i in range(len(list_with_ties)):
        if same_as_next[i] == True:
            count+=1
        else:
            tie_counts.extend([count for i in range(count)])
            count =1
    return tie_counts

def compute_avg_ranks(tie_counts):
    ranks=[]
    i=0
    while len(ranks)<len(tie_counts):
        rank = [(2*i+tie_counts[i]+1)/2 for j in range(tie_counts[i])]
        i+=tie_counts[i]
        ranks.extend(rank)
    return ranks

def get_tie_list(index_list, value_list):
    count_eq=1
    value=value_list[0]
    tie_indices={}
    for i in range(1,len(value_list)):
        if value_list[i]==value:
            count_eq+=1
        else:
            for j in range(count_eq):
                tie_indices[index_list[i-j-1]]=set([index_list[k] for k in range(i-count_eq,i)])
                tie_indices[index_list[i-j-1]].remove(index_list[i-j-1])
            value=value_list[i]
            count_eq=1
    i+=1
    for j in range(count_eq):
        tie_indices[index_list[i-j-1]]=set([index_list[k] for k in range(i-count_eq,i)])
        tie_indices[index_list[i-j-1]].remove(index_list[i-j-1])
    return tie_indices

def count_con_dis_diff(list_to_sort,tie_indices):
    node_data = {'con':np.zeros(len(list_to_sort)), 'dis':np.zeros(len(list_to_sort))}
    lists_to_merge = [[value] for value in list_to_sort]
    index_lists = [[i] for i in range(len(list_to_sort))]

    while len(lists_to_merge)>1:
        merged_lists = []
        merged_indicies = []
        for i in range(int(len(lists_to_merge)/2)):
            merged, indices = merge_list(lists_to_merge[2*i],lists_to_merge[2*i+1],
                                         index_lists[2*i],index_lists[2*i+1], node_data, tie_indices)
            merged_lists.append(merged)
            merged_indicies.append(indices)
        if len(lists_to_merge) % 2 != 0:
            merged_lists.append(lists_to_merge[-1])
            merged_indicies.append(index_lists[-1])
        lists_to_merge = merged_lists
        index_lists = merged_indicies
    tie_counts = count_ties(lists_to_merge[0])
    rank_B = compute_avg_ranks(tie_counts)
    return_data = pd.DataFrame({'index':index_lists[0], 'rank_B':rank_B})
    return_data.sort_values('index', inplace=True)
    return_data.set_index('index', inplace=True)
    return_data['concordant']=node_data["con"]
    return_data['discordant']=node_data["dis"]
    return return_data

def merge_list(left,right, index_left, index_right, node_data,tie_indices):
    merged_list = []
    merged_index = []
    while ((len(left)>0) & (len(right)>0)):
        if left[0]>=right[0]:
            merged_list.append(left[0])
            merged_index.append(index_left[0])
            #####
            non_ties=np.array(list(set(index_right)-tie_indices[index_left[0]])).astype('int')
            node_data['con'][non_ties]+=1
            node_data['con'][index_left[0]]+=len(non_ties)
            #####
            del left[0], index_left[0]
        else:
            merged_list.append(right[0])
            merged_index.append(index_right[0])
            ####
            non_ties=np.array(list(set(index_left)-tie_indices[index_right[0]])).astype('int')
            node_data['dis'][non_ties]+=1
            node_data['dis'][index_right[0]]+=len(non_ties)
            ####
            del right[0], index_right[0]
    
    if len(left)!=0:
        merged_list.extend(left)
        merged_index.extend(index_left)
        
    elif len(right)!=0:
        merged_list.extend(right)
        merged_index.extend(index_right)
    return merged_list, merged_index


def fast_weighted_kendall(x, y):
    """Weighted Kendall's Tau O(n*logn) implementation. The input lists should contain all nodes."""
    # Anna switched list_a and list_b in her implementation
    list_a, list_b = y, x
    data_table = pd.DataFrame({'A':list_a, 'B':list_b})
    data_table.to_csv("/home/fberes/wkendall_test.csv",index=False)
    data_table['rank_A'] = tiedrank(list_a)
    data_table = data_table.sort_values(['A', 'B'], ascending=False)
    data_table.reset_index(inplace=True,drop=True)
    data_table['index']=data_table.index
    possible_pairs=len(data_table)-1
    
    tie_list_A =get_tie_list(data_table.index,data_table['A'])
    data_table['no_tie_A']=data_table['index'].apply(lambda x: possible_pairs-len(tie_list_A[x]))
    sorted_B_index = np.array(data_table['B']).argsort()
    sorted_B = np.array(data_table['B'])[sorted_B_index]
    tie_list_B = get_tie_list(sorted_B_index, sorted_B)
    data_table['no_tie_B']=data_table['index'].apply(lambda x: possible_pairs-len(tie_list_B[x]))
    data_table.drop('index', inplace=True, axis=1)
    tie_indices = {key:tie_list_A[key]|tie_list_B[key] for key in tie_list_A}
    
    list_to_sort=list(data_table['B'])
    con_dis_data = count_con_dis_diff(list_to_sort,tie_indices)
    
    data_table = pd.concat([data_table,con_dis_data], axis=1)
    numW = sum(data_table.apply(lambda x: 1/x['rank_A']*(x['concordant']-x['discordant']), axis=1))
    denomX = sum(data_table.apply(lambda x: 1/x['rank_A']*(x['no_tie_A']), axis=1))
    denomY = sum(data_table.apply(lambda x: 1/x['rank_B']*(x['no_tie_B']), axis=1))
    #print(denomX, denomY, numW)
    return data_table, numW/math.sqrt(denomX*denomY)