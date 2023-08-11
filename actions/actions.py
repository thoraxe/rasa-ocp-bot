# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List

import requests,simplejson,re

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class CallLLM(Action):

     def name(self) -> Text:
         return "action_call_llm"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        #print(f"Domain: {simplejson.dumps(domain)}")
        #tracker_state = tracker.current_state()

        tracker_slots = tracker.current_slot_values()

        #print(f"Tracker state: {simplejson.dumps(tracker_state)}")
        print(f"Tracker slots: {simplejson.dumps(tracker_slots)}")

        # {"deployment_name": "jj", "min_hpa_replicas": "2", "max_hpa_replicas": "6", 
        # "cpu_memory_utilization": "cpu utilization", "cpu_memory_utilization_target": "80", "requested_slot": null, "session_started_metadata": null}
        deployment_name = tracker_slots["deployment_name"]
        min_hpa_replicas = tracker_slots["min_hpa_replicas"]
        max_hpa_replicas = tracker_slots["max_hpa_replicas"]
        cpu_memory_utilization = tracker_slots["cpu_memory_utilization"]
        cpu_memory_utilization_target = tracker_slots["cpu_memory_utilization_target"]

        llm_prompt = f"kubernetes yaml for a HorizontalPodAutoscaler for a \
deployment named {deployment_name} using a minimum replica count of \
{min_hpa_replicas} and a maximum replica count of {max_hpa_replicas} \
and targeting {cpu_memory_utilization} of \
{cpu_memory_utilization_target} percent"

        llm_prompt_json = '{"prompt":"' + llm_prompt + '"}'
        print(llm_prompt_json)

        result = None

        try:
            result = requests.post(
                url="http://localhost:8080/prompt_request",
                data=llm_prompt_json
            ).json()
        except Exception as e:
            print(f"An Exception occured while handling response from the Advisor API: {e}")

        print(f"Results: {simplejson.dumps(result)}")
        print(f"Results output: {result['output']}")
        raw_output = result["output"]

        # strip backticks
        initial_stripped_output = re.sub(r'^[`\s]+|[`\s]+$', '', raw_output) 

        # strip frontmatter
        clean_output = re.sub('^.*?\\n.*?', '', initial_stripped_output)

        dispatcher.utter_message(text=clean_output)

        return []
