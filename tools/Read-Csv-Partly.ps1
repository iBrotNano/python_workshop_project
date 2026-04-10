# Extracts a specified number of lines from an input CSV file and saves them to an output CSV file. 
# This helps in working with large CSV files by allowing you to read only a portion of the data for testing or analysis purposes.

param(
    [string]$InputFile = "input.csv",
    [string]$OutputFile = "output.csv",
    [int]$LinesToRead = 100
)

Get-Content $InputFile -TotalCount $LinesToRead | Set-Content $OutputFile