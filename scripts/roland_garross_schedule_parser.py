from bs4 import BeautifulSoup
import os, sys
import pandas as pd
import datetime


def get_date_from_title(title):
    day, rest = title.split(":")
    weekday, rest = rest.split(",")
    date, rest = rest.split(" Schedule")
    date = datetime.datetime.strptime(date.strip().rstrip("e"), '%d %b').replace(year=2017).date()
    return day, date

def get_court_params(court):
    courtName, matches = court.contents
    if len(courtName.div.contents) == 2:
        court_name, start_en = courtName.div.contents
    else:
        court_name, _, start_en, _ = courtName.div.contents
    court_name = court_name.strip("\n")
    start_en = start_en.string
    return matches, court_name, start_en

def get_results(match):
    result = match.find("div", {"class": "result"})
    teams, _, matchScore = result.contents
    teams, _, teams_opponent = teams.contents
    teams = [item.string for item in teams.findAll("a")]
    teams_opponent = [item.string for item in teams_opponent.findAll("a")]
    matchScore = matchScore.string.strip("\n") if matchScore.string is not None else "Cancelled"
    return teams, teams_opponent, matchScore

def main(schedule_folder, output_folder):
    html_files = [f for f in os.listdir(schedule_folder) if f.endswith(".html")]
    html_files = sorted(html_files, key=lambda s: int(s.rstrip(".html").lstrip("schedule")))

    cols = ["day", "date", "courtName", "orderNumber", "matchHeader", "startDate", "playerName active", "playerName opponent", "matchScore"]
    schedule_df = pd.DataFrame(columns=cols)

    for html_file in html_files:
        print(html_file)
        with open(schedule_folder + html_file) as fin:
            soup = BeautifulSoup(fin.read(), "html.parser")
        title = soup.title.string.strip("\n")
        day, date = get_date_from_title(title)
        for court in soup.findAll("div", {"class": "court"}):        
            matches, court_name, start_en = get_court_params(court)
            for i in range(len(matches.contents)):
                match = matches.contents[i]
                matchHeader = match.find("div", {"class": "matchHeader"}).span.string
                teams, teams_opponent, matchScore = get_results(match)
                if len(teams) == len(teams_opponent) and len(teams) in [1,2]:
                    for idx in range(len(teams)):
                        new_row = {"day": day, "date": date, "courtName": court_name, "orderNumber": i+1, "matchHeader": matchHeader, 
                               "startDate": start_en, "playerName active": teams[idx], "playerName opponent": teams_opponent[idx], "matchScore": matchScore}
                        schedule_df = schedule_df.append(new_row, ignore_index=True)
                else:
                    raise RuntimeError("Invalid player number occured!")
    print("writing...")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    schedule_df.to_csv("%s/schedule_df.csv" % output_folder, sep="|", index=False, header=True, encoding='utf-8')

if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(schedule_folder=sys.argv[1], output_folder=sys.argv[2])
    else:
        print("Running HTML parser with DEFAULT parameters!")
        script_path = os.path.realpath(__file__)
        repo_folder = "/".join(script_path.split("/")[:-2])
        main(schedule_folder="%s/data/raw/schedule/" % repo_folder, output_folder="%s/data/preprocessed/" % repo_folder)
    print("Parsing HTML files ENDED.")