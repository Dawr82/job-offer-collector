import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt

import fetch
import parse


class ContentPrinter:

    """Responsible for displaying content part of the website."""

    def __init__(self, data_raw):
        self.data_raw = data_raw

    def content(self, choice):
        data = fetch.prepare(self.data_raw)
        if choice == "About":
            self.about()
        elif choice == "Job offers":
            self.offers(data)
        elif choice == "Summary":
            self.summary(data)

    def about(self):
        st.title("About this webiste")
        st.write(
            """
        Here you can find some information regarding IT job offers in Poland.\n
        Navigate through the website using sidebar options.\n  
        Feel free to contact me on dskorupa05@gmail.com, if you wish.
        """
        )

    def offers(self, data):
        data_cl = data[
            ["position", "category", "salary (PLN)", "seniority", "locations"]
        ]
        unique_locations = parse.get_unique_locations(self.data_raw)
        unique_seniority = parse.get_unique_seniority(self.data_raw)
        st.title("IT job offers in Poland")
        selected_cat = st.multiselect("Select categories", data["category"].unique())
        selected_loc = st.multiselect("Select locations", unique_locations)
        selected_sen = st.radio("Select seniority level", unique_seniority)
        if selected_cat:
            data_cl = data_cl[data_cl.category.isin(selected_cat)]
        if selected_loc:
            data_cl = data_cl.loc[
                data_cl["locations"].str.contains("|".join(selected_loc))
            ]
        if selected_sen:
            if selected_sen != "All":
                data_cl = data_cl.loc[
                    data_cl["seniority"].str.contains("|".join(selected_sen.split(",")))
                ]
        st.caption(f"Job offers in total: {data_cl.shape[0]}")
        st.dataframe(data_cl, height=600)

    def summary(self, data):
        st.title("Job offer insights")
        plt.style.use("ggplot")
        self.__summary_draw_metrics(data)
        self.__summary_draw_tech()
        self.__summary_draw_seniority()

    def __summary_draw_metrics(self, data):
        category_counts = iter(
            fetch.get_data_req(
                fetch.API_SERVER_URL_TEMPLATE.format(
                    count_by="category", sort_order="desc"
                )
            )
        )
        most_common_1 = next(category_counts)
        most_common_2 = next(category_counts)
        most_common_3 = next(category_counts)

        remote_prc = round(
            (data["locations"].value_counts()["Remote"] / data.index.size) * 100, 2
        )
        english_prc = round(
            (
                fetch.get_data_req(
                    fetch.API_SERVER_URL_TEMPLATE.format(
                        count_by="required", sort_order="desc"
                    )
                )["English"]
                / data.index.size
            )
            * 100,
            2,
        )

        cols = st.columns(3)
        with cols[0]:
            st.metric("1st most wanted category", most_common_1)
            st.metric("Entirely remote", str(remote_prc) + "%")
        with cols[1]:
            st.metric("2nd most wanted category", most_common_2)
            st.metric("English required", str(english_prc) + "%")
        with cols[2]:
            st.metric("3rd most wanted category", most_common_3)

    def __summary_draw_tech(self):
        tech_counts = fetch.get_data_req(
            fetch.API_SERVER_URL_TEMPLATE.format(count_by="required", sort_order="desc")
        )
        most_common_tech = {}
        for key, val in tech_counts.items():
            if key not in parse.SOFT_SKILLS:
                most_common_tech[key] = val
            if len(most_common_tech) > 10:
                break
        fig, ax = plt.subplots()
        ax.barh(
            list(reversed(list(most_common_tech.keys()))),
            list(reversed(most_common_tech.values())),
        )
        st.subheader("10 Most demanded technologies")
        st.write("The below bar chart presents 10 most looked for technologies.")
        st.pyplot(fig)

    def __summary_draw_seniority(self):
        seniority_counts = fetch.get_data_req(
            fetch.API_SERVER_URL_TEMPLATE.format(
                count_by="seniority", sort_order="desc"
            )
        )
        explode = (0, 0, 0.15, 0, 0)
        fig, ax = plt.subplots()
        ax.pie(
            seniority_counts.values(),
            labels=seniority_counts.keys(),
            explode=explode,
            autopct="%1.1f%%",
            startangle=260,
            shadow=True,
        )

        st.subheader("Seniority vs job offers")
        st.write("Who has the biggest pool to choose from?")
        st.pyplot(fig)


def sidebar():
    with st.sidebar:
        choice = option_menu(
            "What's next?",
            ["About", "Job offers", "Summary"],
            icons=["house", "list-ul", "card-text"],
            menu_icon="app-indicator",
        )
    return choice


if __name__ == "__main__":
    data = fetch.get_data_req(fetch.API_SERVER_URL_BASE)
    if data is None or not data:
        st.title("Nothing to show :(")
    else:
        choice = sidebar()
        content_printer = ContentPrinter(data)
        content_printer.content(choice)
