import requests


class InventoryHandler:

    URL = 'https://djoinventory.rmoesbergen.nl/api/v1'

    def __init__(self):
        pass

    def search(self, keyword):
        result = requests.get(self.URL + '/items/search/{0}'.format(keyword))
        print(result)
        if not result.ok:
            return "Er ging iets mis!"

        items = result.json()['items']
        image = None
        for item in items:
            location_id = item['location_id']
            image = self.URL + "/location/{0}/photo".format(location_id)

            response = "Gevonden: {0} ({1})\n".format(item['name'], item['description'])
            response += "Locatie: {0}, ".format(item['location_description'])
            break
        else:
            response = "Helaas, niets gevonden!"

        return response, image

    def search_many(self, keyword):
        result = requests.get(self.URL + '/items/search/{0}'.format(keyword))
        print(result)
        if not result.ok:
            return False # dit zou beter kunnen. exception?

        items = result.json()['items']

        results = []
        for item in items:
            location_id = item['location_id']
            image = self.URL + "/location/{0}/photo".format(location_id)

            response = "Gevonden: {0} ({1})\n".format(item['name'], item['description'])
            response += "Locatie: {0}, ".format(item['location_description'])
            results.append((item['name'], item['description'], item['location'], image))

        if len(results) == 0:
            return False

        return results
