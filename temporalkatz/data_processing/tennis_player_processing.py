import editdistance
import numpy as np
import pandas as pd
import json, pytz

def load_dataset_parameters(dataset_id):
    """Load dataset specific parameters. Choose from 'rg17' or 'uo17' dataset_id values."""
    if dataset_id == "uo17":
        # There was no tennis match on 2017-08-26,27!
        min_epoch = 1503288000
        dates = ["2017-08-%.2i" % i for i in range(21,32)] + ["2017-09-%.2i" % i for i in range(1,11)]
        missing_dates = ["2017-08-21","2017-08-26","2017-08-27"]
        time_zone = pytz.timezone('America/New_York')
        sep = ";"
    elif dataset_id == "rg17":
        # There was no tennis match on 2017-05-27!
        min_epoch = 1495584000
        dates = ["2017-05-%.2i" % i for i in range(24,32)] + ["2017-06-%.2i" % i for i in range(1,12)]
        missing_dates = ["2017-05-27"]
        time_zone = pytz.timezone('Europe/Paris')
        sep = "|"
    else:
        raise RuntimeError("Invalid dataset!")
    return min_epoch, len(dates), dates, missing_dates, time_zone, sep

### player assigments ###

def update_matches(true_matches,df,screen_name_col="screen_name"):
    """Update true player-account matches"""
    for index, row in df.iterrows():
        name, values = row["schedule_name"], set(row[screen_name_col])
        if not name in true_matches:
            true_matches[name] = values
        else:
            true_matches[name] = true_matches[name].union(values)

def print_coverage(matches_dict, schedule_name_counter, data_screen_names):
    """Calculate coverage for the given data"""
    num_found_in_data = 0
    for k in matches_dict:
        if k in schedule_name_counter and len(matches_dict[k].intersection(data_screen_names)) > 0:
            num_found_in_data += 1
    print(num_found_in_data, len(schedule_name_counter), num_found_in_data / len(schedule_name_counter))
            
def export_matches(match_dict, file_name_prefix):        
    """Export player-account dictionary"""
    true_matches_screen_names = []
    true_matches_copy = {}
    for player in match_dict:
        true_matches_copy[player] = list(match_dict[player])
        true_matches_screen_names += true_matches_copy[player]
    
    with open("%s.json" % file_name_prefix, "w") as f:
        json.dump(true_matches_copy, f, sort_keys=True, indent=3)
    
    with open("%s_screen_names.json" % file_name_prefix, "w") as f:
        json.dump(true_matches_screen_names, f)

### edit distance ###

def cast_to_lower(val):
    return str(val).lower()

def remove_spaces(val):
    return str(val).replace(" ","")

def eval_edit_dist(reference, comparable, use_lower, remove_space):
    """Calculate edit distance between words. The comparison can be made after lowercasing or space-removing."""
    vals = reference, comparable
    if use_lower:
        vals = list(map(cast_to_lower, vals))
    if remove_space:
        vals = list(map(remove_spaces, vals))
    #print(vals)
    return editdistance.eval(vals[0], vals[1])

def calculate_edit_distance_matrix(reference_values, search_values, use_lower=True, remove_space=True):
    """Calculate edit distance matrix with lowercasing and space-removal (optinal).
       Rows: tennis player names from schedule (reference)
       Columns: Twitter account names (screen_name) or displayed name of the account
    """
    row_size, col_size = len(reference_values), len(search_values)
    edit_distances = np.zeros((row_size, col_size))
    for i in range(row_size):
        reference = reference_values[i] # try to find match for real tennis player in the schedule...
        res = list(map(lambda x: eval_edit_dist(reference, x, use_lower=use_lower, remove_space=remove_space), search_values))
        edit_distances[i,:] = res
    return edit_distances

def process_edit_distances(mx, reference_counter, reference_values, search_values):
    """Extract search values that has minimum edit distance from reference values. Multiple hits are enabled."""
    min_distances = mx.min(axis=1)
    matches = []
    for i in range(mx.shape[0]):
        min_dist = min_distances[i]
        min_indices = np.argwhere(mx[i,:] == min_dist)
        min_indices = list(min_indices[:,0])#convert array to column
        for idx in min_indices:
            reference, min_match = reference_values[i], search_values[idx]
            matches.append((reference, reference_counter[reference], min_match, min_dist))
    return matches

### daily players ###

def leave_boy_girl_wheelchair(value):
    n_boy = "Boy" not in value
    n_girl = "Girl" not in value
    n_wheel = "Wheelchair" not in value
    return n_boy and n_girl and n_wheel

def update_match_counts(df, true_matches):
    found_players=set(true_matches.keys())
    df['missing_players'] = df['players'].apply(lambda x: list(set(x)-found_players))
    df["found_players"] = df["players"].apply(lambda p_list: [p for p in p_list if p in true_matches])
    df["count"] = df.apply(lambda x: len(x["players"]), axis=1)
    df["match_count"] = df.apply(lambda x: len(x["found_players"]), axis=1)
    df["mismatch_count"] = df.apply(lambda x: len(x["missing_players"]), axis=1)
    
def get_daily_players(schedule_df, matches_dict, schedule_name_counter=None, data_screen_names=None, filter_func=None):
    """Return daily tennis players in dictionary and dataframe based on the schedule and the found player-account assigments."""
    # filtering the matches
    if schedule_name_counter is None or data_screen_names is None:
        print("No filtering will be applied!")
        true_matches = matches_dict
    else:
        true_matches = {}
        for k in matches_dict:
            if k in schedule_name_counter and len(matches_dict[k].intersection(data_screen_names)) > 0:
                true_matches[k] = matches_dict[k].intersection(data_screen_names)
    # creating dataframe
    if filter_func == None:
        schedule_df_tmp = schedule_df
    else:
            schedule_df_tmp = schedule_df[schedule_df["matchHeader"].apply(filter_func)]
    daily_players = {}
    for index, row in schedule_df_tmp.iterrows():
        date, winner, loser = row["date"], row["playerName active"], row["playerName opponent"]
        header, court, match = row["matchHeader"], row["courtName"], row["orderNumber"]
        match_id = "%s_%s_%i" % (header, court, match)
        if not date in daily_players:
            daily_players[date] = {}
        daily_players[date][winner] = match_id
        daily_players[date][loser] = match_id
    # daily players grouped
    daily_players_grouped = [(key, set(daily_players[key].keys())) for key in daily_players]
    daily_players_df = pd.DataFrame(daily_players_grouped, columns=["date", "players"])
    update_match_counts(daily_players_df, true_matches)
    daily_players_df = daily_players_df.sort_values("date").reset_index(drop=True)
    return daily_players, daily_players_df


