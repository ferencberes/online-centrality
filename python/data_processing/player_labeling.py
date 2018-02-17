import pandas as pd
import json, datetime, sys, os

sys.path.insert(0,"../")
from centrality_utils.base_computer import scores2file

### Time Conversions ###

def epoch2date(epoch, tz_info=None):
    """Convert epoch to date based on timezone information. If 'tz_info==None' then local timezone information is used."""
    if tz_info == None:
        dt = datetime.datetime.fromtimestamp(epoch)
    else:
        dt = datetime.datetime.fromtimestamp(epoch, tz=tz_info)
    return "%i-%.2i-%.2i" % (dt.year, dt.month, dt.day)

### Identifier mappings ###

def filter_assigments(all_player_dict, schedule_name_counter, data_screen_names):
    """Keep only dataset related player assigments"""
    player_dict = {}
    for p in all_player_dict:
        if schedule_name_counter is None:
            player_dict[p] = all_player_dict[p]
        else:
            if p in schedule_name_counter:
                if data_screen_names is None:
                    player_dict[p] = all_player_dict[p]
                else:
                    accounts = list(set(all_player_dict[p]).intersection(set(data_screen_names)))
                    if len(accounts) > 0:
                        player_dict[p] = accounts
    print("Total number of assigments: %i" % len(all_player_dict))
    print("Dataset related number of assigments: %i" % len(player_dict))
    return player_dict

def load_player_account_assigments(assigment_file_path, schedule_name_counter=None, data_screen_names=None):
    """Load player-account assigments."""
    with open(assigment_file_path) as f:
        all_player_dict = json.load(f)
    players_dict = filter_assigments(all_player_dict, schedule_name_counter, data_screen_names)
    multiple_acc_count = 0
    for name in players_dict:
        if len(players_dict[name]) > 1:
            multiple_acc_count += len(players_dict[name]) - 1
    print("Number of multi-player accounts: %i" % multiple_acc_count)
    print("Number of players: %i" % len(players_dict))
    print("Number of accounts: %s" % (len(players_dict) + multiple_acc_count))
    return players_dict

def get_screen2id_dict(df,reverse=False):
    """Based on Twitter mention data this function returns 'screen_name' -> Twitter 'user_id' mapping dictionary."""
    if reverse:
        src = dict(zip(df["src"],df["src_screen_str"]))
        trg = dict(zip(df["trg"],df["trg_screen_str"]))
    else:
        src = dict(zip(df["src_screen_str"],df["src"]))
        trg = dict(zip(df["trg_screen_str"],df["trg"]))
    src.update(trg)
    return src

def get_screen_name_to_player(players_dict):
    """Based on player-account assigments this function returns 'screen_name' -> schedule player name mapping."""
    screen_name_to_player = {}
    for player in players_dict:
        for screen_name in players_dict[player]:
            if screen_name in screen_name_to_player:
                raise RuntimeError("screen_name duplication for '%s' is note allowed!" % screen_name)
            else:
                screen_name_to_player[screen_name] = player
    return screen_name_to_player

def get_recoder_dict(recoder_file_path, verbose=True):
    """Returns a dictionary which maps Twitter 'user_id' to 'generated_id'."""
    recoder_df = pd.read_csv(recoder_file_path, sep=" ")
    if verbose:
        print(recoder_df.head(3))
    return dict(zip(recoder_df["original_id"],recoder_df["generated_id"]))

### Labeling Users ###

def get_daily_users_dict(collected_dates, mentions_df, last_date):
    """Store 'screen_name' -> Twitter 'user_id' mapping for each day"""
    daily_users_dict = {}
    print("Storing players by date STARTED!")
    for date in collected_dates:
        print(date)
        daily_df = mentions_df[mentions_df["date"] == date]
        if len(daily_df) == 0:
            daily_users_dict[date] = {}
        else:
            daily_users_dict[date] = get_screen2id_dict(daily_df)
        if date == last_date:
            break
    print("Storing players by date FINISHED.")
    return daily_users_dict

def set_label_value(label_value_dict, user, date_idx, collected_dates, screen_name_to_player, daily_found_player_dict):
    label = 0.0
    if user in screen_name_to_player:
        if screen_name_to_player[user] in daily_found_player_dict[collected_dates[date_idx]]:
            label = label_value_dict["current"]
        elif date_idx > 0 and screen_name_to_player[user] in daily_found_player_dict[collected_dates[date_idx-1]]:
            label = label_value_dict["previous"]
        elif date_idx < len(collected_dates)-1:
            next_date = collected_dates[date_idx+1]
            if next_date in daily_found_player_dict and screen_name_to_player[user] in daily_found_player_dict[next_date]:
                label = label_value_dict["next"]
    return label

def get_daily_label_dicts(label_value_dict, collected_dates, mentions_df, mapper_dicts, last_date=None, missing_dates=None):
    """Label users in mention data based on schedule. Give label 1 to daily tennis players and 0 otherwise."""
    recoder_dict, screen_name_to_player, daily_found_player_dict = mapper_dicts
    #daily_users_dict = get_daily_users_dict(collected_dates, mentions_df, last_date)
    user_dict = get_screen2id_dict(mentions_df)
    daily_label_dicts = {}
    print("Labeling users STARTED!")
    for date_idx, date in enumerate(collected_dates):
        print(date)
        label_dict = {}
        for user in user_dict:
            origi_user_id = user_dict[user]
            recoded_user_id = recoder_dict[origi_user_id]
            label_dict[recoded_user_id] = set_label_value(label_value_dict, user, date_idx, collected_dates, screen_name_to_player, daily_found_player_dict)
        daily_label_dicts[date] = label_dict
        if date == last_date:
            break
    print("Labeling users FINISHED!")
    return daily_label_dicts

### Export Labels ###

def export_label_files(player_output_dir, collected_dates, daily_label_dicts, last_date=None, only_pos_label=True, first_index=0):
    """Export label files for each date."""
    if not os.path.exists(player_output_dir):
        os.makedirs(player_output_dir)
        print("%s folder was created." % player_output_dir)
    i = first_index
    for date in collected_dates:
        sorted_user_labels = []
        for u in sorted(daily_label_dicts[date].keys()):
            if only_pos_label:
                # export only positive user labels
                if daily_label_dicts[date][u] > 0.0:
                    sorted_user_labels.append((u, daily_label_dicts[date][u]))
            else:
                sorted_user_labels.append((u, daily_label_dicts[date][u]))
        scores2file(sorted_user_labels,"%s/players_%i.csv" % (player_output_dir, i))
        i += 1
        if date == last_date:
            break
            
def export_recoded_player_ids(output_prefix, screen_to_id, screen_name_to_player, recoder_dict):
    """Export only those recoded ids where the correcponding screen_name was in the dataset."""
    recoded_found_ids = []
    not_found_cnt = 0
    for screen_name in screen_name_to_player:
        if screen_name in screen_to_id:
            original_id = screen_to_id[screen_name]
            recoded_id = recoder_dict[original_id]
            recoded_found_ids.append(recoded_id)
        else:
            not_found_cnt += 1
            print("'%s' is not in the data!" % screen_name)
    print("Number of screen_names in the data: %i" % len(recoded_found_ids))
    print("%i screen_names were not found in the data." % not_found_cnt)
    export_recoded_ids(output_prefix, recoded_found_ids)
    
def export_recoded_ids(output_prefix, recoded_found_ids):    
    with open("%s/recoded_player_accounts.txt" % output_prefix,'w') as f:
        for val in sorted(recoded_found_ids):
            f.write("%i\n" % val)
    print("Export FINISHED.")