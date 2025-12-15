# U.S. Labor Structure Dashboard: Project Write-up

## Introduction
The goal of this project was to build a complete, reproducible data product that explores key trends in the U.S. labor market using official data from the Bureau of Labor Statistics (BLS). Rather than focusing on a single indicator, the project examines **key trends in the U.S. labor market over time**, combining unemployment and labor force participation with structural changes in employment, such as manufacturing’s share of total nonfarm employment.  

This project required moving through the entire data workflow: planning the analysis, collecting raw data from an external API, cleaning and transforming the data, building an interactive dashboard, and organizing everything so it can be reproduced on another computer through GitHub. While I have experience building dashboards in R using Shiny and Flexdashboard, this was my first time implementing a full pipeline using Python, Streamlit, and GitHub-based deployment.

## Data and Methods
All data used in this project comes from the Bureau of Labor Statistics (BLS), which provides publicly available labor market statistics through its API. The main series used in the dashboard include the unemployment rate and labor force participation from the Current Population Survey (CPS) and employment levels from the Current Employment Statistics (CES) program. Manufacturing employment and total nonfarm payroll employment are used together to calculate manufacturing’s share of total employment.  

A key part of the project was learning to work directly with an API. The BLS API returns data in a nested JSON format that is not immediately suitable for analysis. I wrote a Python script to request the data in manageable time chunks, convert the JSON responses into a tabular format, and merge the series into a single dataset indexed by date. This dataset is saved as a CSV file, which is then read by the Streamlit dashboard.  

Because different BLS series begin in different years and may have missing values, I handled gaps carefully. Forward-filling employment series ensured consistent calculations, especially when computing manufacturing’s share of employment. This step reinforced the importance of understanding the structure and limitations of economic data, not just running code blindly.

## Key Observations from the Data
One of the most striking patterns is the spike in the unemployment rate in 2020. After remaining relatively stable in the years leading up to 2020, unemployment rose sharply, reflecting the onset of the COVID-19 pandemic.  

In addition, labor force participation declined noticeably around the same period. Although the dashboard focuses on unemployment and employment shares, this decline highlights how many individuals left the labor force entirely during 2020, reflecting health concerns, caregiving responsibilities, and reduced job availability. Together, these patterns show that unemployment and labor force participation trends provide important context for understanding labor market health over time.  

The manufacturing share of employment provides a longer-run perspective. Unlike unemployment, which shows noticeable spikes during certain years, manufacturing’s share exhibits a gradual downward trend over time. This reflects structural changes such as automation, globalization, and the expansion of the service sector. By placing this long-run trend next to unemployment and labor force participation trends, the dashboard helps distinguish between cyclical events and deeper structural changes.

## Dashboard Design and Implementation
The Streamlit dashboard was designed to be simple and intuitive. Users can select a start year and end year to focus on a specific time period, and the dashboard automatically calculates how much the unemployment rate, labor force participation, and manufacturing employment share changed over that window. Visual indicators, such as up and down arrows, help communicate whether these changes represent increases or decreases.  

One design choice I found especially valuable was showing the manufacturing share formula directly in the dashboard. Displaying the calculation ensures transparency and makes it clear that this metric is derived from two underlying employment series rather than being an official standalone BLS statistic. This reinforces good analytical practice and helps users interpret the results correctly.  

Compared to my previous experience with R Shiny and Flexdashboard, building this project in Python and Streamlit felt more focused on modularity and deployment. Separating the data-fetching script from the visualization code made the project easier to maintain and update. Organizing everything within a GitHub repository also encouraged better code structure, documentation, and reproducibility.

## What I Learned
This project taught me several important lessons. I gained a deeper understanding of U.S. labor market data, particularly how different surveys measure different aspects of employment. Seeing how unemployment, labor force participation, and manufacturing trends move over time improved my intuition about economic indicators.  

I also learned how to build a complete, end-to-end data product using GitHub. Managing dependencies, structuring directories, and ensuring the code could run on another computer were new challenges. This experience highlighted the importance of reproducibility and version control in real-world data work.  

Finally, working with Streamlit showed me how quickly an interactive dashboard can be built once the data pipeline is solid. Rather than focusing only on static plots, I created a tool that allows users to explore the data dynamically and draw their own conclusions.

## What I Would Do Differently
If I were to do a similar project again, I would consider adding more labor force indicators, such as employment-to-population ratios, to provide a more complete picture of labor market health. I would also explore adjusting some series for seasonality, particularly for comparisons across months.  

In addition, I would prioritize automated updates and deployment earlier in the project timeline. Building this workflow from the start would save time and reduce debugging later on.

## Conclusion
Overall, this project was a valuable learning experience that combined economic analysis with practical data engineering skills. It reinforced concepts I had learned previously while pushing me to work with new tools and workflows. Most importantly, it showed how data skills can be applied to real-world economic questions. Going forward, I am excited to continue developing projects like this and applying these skills in professional, real-world settings.
