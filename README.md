# Ukulele Interface

## Overview
The Ukulele Interface is a graphical user interface (GUI) application built using Python's Tkinter library. This application allows users to upload and analyze data related to ukulele songs, including song details, play counts, and requests. The application provides various features such as filtering, sorting, and visualizing data through charts.

## Features
- Upload multiple CSV files containing song data.
- Validate uploaded files to ensure required columns are present.
- Filter and sort data based on user-defined criteria.
- Generate various types of plots to visualize song data.
- Save generated plots as PDF files.

## Requirements
To run this project, you will need the following Python libraries:
- pandas
- numpy
- matplotlib
- tkcalendar
- Pillow

You can install the required libraries using pip:

```bash
pip install pandas numpy matplotlib tkcalendar Pillow


The project requires the following CSV files to function correctly:

tabdb.csv: Contains tab details for songs.
playdb.csv: Contains play count data for songs.
requestdb.csv: Contains request data for songs.
Make sure to have these files in the same directory as the script.
