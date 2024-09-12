# Overview

Python scripting example for the Dynatrace API utilizing the [Dynatrace Python API Client](https://github.com/dynatrace-oss/api-client-python) from the Dynatrace OSS team.

The script `problems.py` will call the get problems API and output the results in to a CSV file called `problems.csv`.  This CSV file can then be used in Excel to make a chart from the data.

## Requirements

* Dynatrace API Token with `v2 Read Problems` scope
* Python 3.x.x. (I used 3.9.12)
* pip (I used 22.1)
* The Dynatrace Python API Client library
  ```
  pip install dt
  ```
  
## Usage

1. Export the Dynatrace URL and API Token as environment variables

    ```
    export DT_BASE_URL="http://[YOUR-TENANT].live.dynatrace.com"
    export DT_API_TOKEN="[YOUR-TOKEN]"
    ```
    
1. Review and adjust as needed the logic in `problems.py` for the filters that are defined in the [Dynatrace get problems API docs](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/problems-v2/problems/get-problems-list) 

    Examples:
    
    ```
    problems = dt.problems.list(time_from="now-30m",problem_selector='status("closed")')
    problems = dt.problems.list(time_from="now-180d",problem_selector='status("closed"),managementZoneIds("mZId-1", "mzId-2")')
    problems = dt.problems.list(time_from="now-120m",problem_selector='affectedEntityTypes("CUSTOM_DEVICE")')
    problems = dt.problems.list(time_from="now-120m",problem_selector='entityTags("key1:value1","key2:value2")')
    ```
    
2. Review and adjust as needed the CSV output.  


3. Adjust date format in the `formatdate` function.

    ```
    # Example: Year then month
    return thedate.strftime("%Y-%m")

    # Example: Day format
    return thedate.strftime("%m/%d/%Y")
    ```

4. Run program and view output
    ```
    python problems.py && cat problems.csv
    ```
    
    Example output:
    ```
    problem, title, status, impact_level, severity_level, start_time, end_time
    P-230227,Availability issue,CLOSED,INFRASTRUCTURE,AVAILABILITY,02/08/2023,02/08/2023
    P-230226,Availability issue,CLOSED,INFRASTRUCTURE,AVAILABILITY,02/08/2023,02/08/2023
    P-230225,Availability issue,CLOSED,INFRASTRUCTURE,AVAILABILITY,02/08/2023,02/08/2023
    ```
  
5. Open `problems.csv` in Excel and make a pivot table from the results.  See the `problems.xlsx` example in this repo.
