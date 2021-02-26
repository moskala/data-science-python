import os
import pandas as pd
from datetime import datetime
from dateutil.parser import parse


def read_dataframes(name):
    """Funkcja wczytuje ramki danych z plików csv w folderze name."""

    folder_boardgames = os.path.join("..", "data", name)
    Posts = pd.read_csv(os.path.join(folder_boardgames, "Posts.xml.csv"))
    Users = pd.read_csv(os.path.join(folder_boardgames, "Users.xml.csv"))
    Comments = pd.read_csv(os.path.join(folder_boardgames, "Comments.xml.csv"))
    return Posts, Users, Comments


def unpack_date(df):
    """Funkcja parsuje datę i rozbija ją na 3 kolumny: rok, miesiąc i dzień."""

    df["CreationDate"] = df["CreationDate"].apply(lambda x: (parse(x).year, parse(x).month, parse(x).day))
    df["CreationYear"] = df["CreationDate"].apply(lambda x: x[0])
    df["CreationMonth"] = df["CreationDate"].apply(lambda x: x[1])
    df["CreationDay"] = df["CreationDate"].apply(lambda x: x[2])
    return df


def prepare_posts(Posts):
    """Funkcja wybiera odpowiednie kolumny z Posts, usuwa nan i parsuje date"""

    posts = Posts[["Id", "PostTypeId", "CreationDate", "OwnerUserId"]].reset_index(drop=True)
    posts = posts.dropna(subset=["OwnerUserId"])
    posts = unpack_date(posts)
    return posts


def prepare_comments(Comments):
    """Funkcja wybiera odpowiednie kolumny z Comments, usuwa nan i parsuje date"""

    comments = Comments[["UserId", "CreationDate"]].reset_index(drop=True)
    comments = unpack_date(comments)
    return comments


def filter_by_year(posts, year):
    """Funkcja filtruje ramkę danych po zadanym roku"""

    return posts.loc[posts.CreationYear >= year]


def set_user_id(row):
    """Funkcja określa ID usera na podstawie 2 kolumn, które mogą mieć wartości 0 (czyli brak ID)"""

    val = 0
    if row.OwnerUserId == 0:
        val = row.UserId
    else:
        val = row.OwnerUserId
    return val


def calculate_activity(row):
    """Funkcja oblicza całkowitą aktywność na podstawie ilości pytań, odpowiedzi i komentarzy"""

    val = row.TotalQuestions + row.TotalAnswers + row.TotalComments
    return val


def merge_activity(posts, comments):
    """Funkcja oblicza ilość danej aktywności dla każdego użytkownika i łączy ramki danych"""

    questions = posts[posts.PostTypeId == 1]
    answers = posts[posts.PostTypeId == 2]

    df_total = pd.DataFrame(posts.groupby(["OwnerUserId"]).size(), columns=["TotalPosts"]).reset_index()
    df_questions = pd.DataFrame(questions.groupby(["OwnerUserId"]).size(), columns=["TotalQuestions"]).reset_index()
    df_answers = pd.DataFrame(answers.groupby(["OwnerUserId"]).size(), columns=["TotalAnswers"]).reset_index()
    df_comments = pd.DataFrame(comments.groupby(["UserId"]).size(), columns=["TotalComments"]).reset_index()

    df = df_total.merge(df_questions, how="left", left_on="OwnerUserId", right_on="OwnerUserId")
    df = df.merge(df_answers, how="left", left_on="OwnerUserId", right_on="OwnerUserId")
    df = df.merge(df_comments, how='outer', left_on="OwnerUserId", right_on="UserId")
    df.fillna(0, inplace=True)

    df["UserId"] = df.apply(lambda row: set_user_id(row), axis=1)

    return df


def create_activity_df(collection_name):
    """Funkcja tworzy ramkę danych z aktywnością użytkowników w roku 2020."""

    Posts, Users, Comments = read_dataframes(collection_name)
    posts = prepare_posts(Posts)
    posts = filter_by_year(posts, 2020)
    comments = prepare_comments(Comments)
    comments = filter_by_year(comments, 2020)
    df_activity = merge_activity(posts, comments)
    df_activity.drop("OwnerUserId", inplace=True, axis=1)
    df_activity["TotalActivity"] = df_activity.apply(lambda row: calculate_activity(row), axis=1)
    df_activity = df_activity.sort_values("TotalActivity", axis=0, ascending=False)
    return df_activity


def get_users(collection_name):
    """Funkcja tworzy ramkę danych dla użytkowników i związanych z nimi dat."""

    Posts, Users, Comments = read_dataframes(collection_name)
    users = Users[["Id", "CreationDate", "LastAccessDate", "DisplayName"]]
    users["LastAccessYear"] = users["LastAccessDate"].apply(lambda x: parse(x).year)
    users["CreationYear"] = users["CreationDate"].apply(lambda x: parse(x).year)
    users["ActiveYears"] = users["LastAccessYear"] - users["CreationYear"] + 1
    return users


def get_new_users_by_year(collection_name):
    """Funkcja oblicza ilość użytkowników na podstawie roku dołączenia do serwisu."""

    users = get_users(collection_name)
    df_new_users_by_year = pd.DataFrame(users.groupby(["CreationYear"]).size(),
                                        columns=["NewUsersNumber"]).reset_index()
    return df_new_users_by_year


def get_percentage_of_active_users(users, year=2020):
    """Funkcja oblicza stosunek aktywnych użytkowników do wszystkich w procentach."""

    all_users_number = users.shape[0]
    all_users_number
    active_users = users[users["LastAccessYear"] >= year]
    active_users_number = active_users.shape[0]
    active_users_number
    p = active_users_number / all_users_number * 100
    return p


def get_ranking(collection_name):
    """Funkcja tworzy ranking aktywnych użytkowników w 2020 roku dla danego serwisu."""

    activity_df = create_activity_df(collection_name)
    users = get_users(collection_name)
    ranking = activity_df.merge(users, how='left', left_on='UserId', right_on='Id')
    ranking = ranking.sort_values("TotalActivity", axis=0, ascending=False)
    ranking = ranking[
        ["UserId", "DisplayName", "CreationYear", "ActiveYears", "TotalActivity", "TotalQuestions", "TotalAnswers",
         "TotalComments"]].head(10)
    return ranking




