import requests


def get_drug_info(drug_name: str):
    try:
        url = (
            "https://api.fda.gov/drug/label.json"
            f"?search=openfda.generic_name:{drug_name}+openfda.brand_name:{drug_name}"
            "&limit=1"
        )

        response = requests.get(url, timeout=8)

        if response.status_code != 200:
            return {
                "success": False,
                "message": f"No data found for this medicine. Status: {response.status_code}"
            }

        data = response.json()

        if "results" not in data or not data["results"]:
            return {
                "success": False,
                "message": "No results found in FDA database."
            }

        result = data["results"][0]

        use = result.get("indications_and_usage", ["Not available"])[0]
        side_effects = result.get("adverse_reactions", ["Not available"])[0]
        warnings = result.get("warnings", ["Not available"])[0]

        return {
            "success": True,
            "use": use[:500],
            "side_effects": side_effects[:500],
            "warnings": warnings[:500]
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "FDA API timeout. Please try again."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

















# import requests

# def get_drug_info(drug_name: str):
#     try:
#         url = (
#             "https://api.fda.gov/drug/label.json"
#             f"?search=openfda.generic_name:{drug_name}+openfda.brand_name:{drug_name}"
#             "&limit=1"
#         )

#         response = requests.get(url, timeout=8)

#         if response.status_code != 200:
#             return {
#                 "success": False,
#                 "message": f"No data found for this medicine. Status: {response.status_code}"
#             }

#         data = response.json()

#         if "results" not in data or not data["results"]:
#             return {
#                 "success": False,
#                 "message": "No results found in FDA database."
#             }

#         result = data["results"][0]

#         use = result.get("indications_and_usage", ["Not available"])[0]
#         side_effects = result.get("adverse_reactions", ["Not available"])[0]
#         warnings = result.get("warnings", ["Not available"])[0]

#         return {
#             "success": True,
#             "use": use[:500],
#             "side_effects": side_effects[:500],
#             "warnings": warnings[:500]
#         }

#     except requests.exceptions.Timeout:
#         return {
#             "success": False,
#             "message": "FDA API timeout. Please try again."
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f"Error: {str(e)}"
#         }