import requests
import time


class InventoryHandler:
    URL = 'https://djoinventory.rmoesbergen.nl/api/v1'

    def __init__(self):
        pass

    def search(self, keyword):
        print(keyword)
        result = requests.get(self.URL + '/items/search/{0}'.format(keyword))
        print(result.content)
        if not result.ok:
            return "Er ging iets mis!"

        items = result.json()['items']
        image = None
        if len(items) > 0:
            item = items[0]
            location_id = item['location_id']
            image = self.URL + "/location/{0}/photo?time={1}".format(location_id, time.time())

            response = "<b>Gevonden</b>: {0} ({1})\n".format(item['name'], item['description'])
            response += "<b>Locatie</b>: {0}".format(item['location_description'])
            if len(item['properties']) > 0:
                response += "\n<b>Eigenschappen</b>: {0}".format(', '.join(item['properties']))
        else:
            response = "Helaas, niets gevonden!"

        return response, image

    def search_many(self, keyword):
        result = requests.get(self.URL + '/items/search/{0}'.format(keyword))
        print(result)
        if not result.ok:
            return False  # dit zou beter kunnen. exception?

        items = result.json()['items']

        results = []
        for item in items:
            location_id = item['location_id']
            image = self.URL + "/location/{0}/photo?time={1}".format(location_id, time.time())

            results.append((item['name'], item['description'], item['location'], image))

        if len(results) == 0:
            return False

        return results
