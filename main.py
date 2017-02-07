import googlemaps
import re 
import csv
import string
from datetime import datetime


class SafeRoute():

	def __init__(self):
		#TODO: Dont forget to add your own google api key
		self.gmaps = googlemaps.Client(key='')
		self.directional_words = ['left','right','west','north','south','east']
		self.directional_chars = ['N','E','S','W']
		#TODO: Finish adding crimanal charges and add weights to all of them
		self.crime_weight      = {'CRIMINAL DAMAGE':'', 'BATTERY':'', 'THEFT':'', 'HOMICIDE':'', 'ASSAULT':''}

	def readFilteredData(self):
		file = open("filtered_data.csv")
		crime_data = csv.reader(file)
		
		self.street_dictionary = {}
		for row in crime_data:
			self.street_dictionary[row[0].lower()] = row[1]

	def readUnfilteredData(self):
		file = open("data.csv")
		crime_data = csv.reader(file)
		
		self.street_dictionary = {}
		for row in crime_data:
			street_name   = row[3][6:].lower()
			crime = row[4]
			weight = self.calculateSingleWeight(crime)
			self.street_dictionary[street_name] = self.street_dictionary.get(street_name, 0) + weight

	def writeFilteredData(self):
		file = open("filtered_data.csv", 'wb')
		crime_data = csv.writer(file)
		for key, value in self.street_dictionary.items():
			street_parsed = re.split(' ', key)
			street = ""

			for s in street_parsed:
				if s == "av":
					street += "ave"
				else:
					street += s

			crime_data.writerow([street, value])

	def getSteps(self, directions):
		return directions['legs'][0]['steps']

	def calculateSingleWeight(self, crime):
		#TODO: need to finish crime weights before we can implement this
		"""
		weight = self.crime_weight.get(crime, 0)
		return weight
		"""
		return 1

	def calculateTotalWeight(self, route):
		total_weight = 0
		for street in route:
			for key, val in self.street_dictionary.items():
				if key == street[0]:
					total_weight += int(val) / street[1]

		return total_weight

	def getBestRoute(self, routes):
		best_route = []
		lowest_weight = 0
		best_route_index = 0
		route_index = 0

		for route in routes:
			weight = self.calculateTotalWeight(route)
			
			if lowest_weight > weight or best_route == []:
				best_route = route
				lowest_weight = weight
				best_route_index = route_index

			route_index = route_index + 1
		
		return [lowest_weight, best_route], best_route_index
		
	def getMainStreet(self, instructions):
		streets = []
		main_street = []
		
		for instruction in instructions:
			street_validity = True
			for directional_word in self.directional_words:
				if directional_word == instruction or instruction.isdigit():
					street_validity = False
					break

			if street_validity:		
				streets.append(instruction)
		
		for street in streets:
			for directional_char in self.directional_chars:
				#Take out the end characters that arent the street name
				if street[-1:] == directional_char:
					street = street[:-1]
				if street[-1:] == ' ':
					street = street[:-1]

				#Take out the begining characters that arent the street name
				if street[:1] == directional_char:
					street = street[1:]
				if street[:1] == ' ':
					street = street[1:]

		#TODO: Check to make sure that the first non direction street is
		#      the main street in all cases. For now we assume this.
		if len(streets):
			main_street = streets[0]

		return main_street.lower()

	def getDuration(self, step):
		return step['duration']['value']


	def printOutput(self, route, steps, origin, destination):
		step_num = 0

		print "The best route has a danger weight of " + str(route[0])
		print "To get from " + origin + " to " + destination + " follow these steps:"

		for step in steps:
			step_num = step_num + 1
			print str(step_num) + ": " + step['html_instructions']
	

def main():
	sf = SafeRoute()

	"""
	Filter data if needed. But there should be a 'filtered_data.csv' included.
	"""
	filter = True

	if filter == True: 
		sf.readUnfilteredData()
		sf.writeFilteredData()

	elif filter == False:
		sf.readFilteredData()


	#Test input
	'''
	origin = '4650 W North Ave, Chicago, IL 60639'
	destination = '1745 W 63rd St, Chicago, IL 60636'
	'''

	print "Welcome to the safe route finder!"
	origin = input('Enter your starting address in Chicago: ')
	destination = input('Enter your ending address in Chigaco: ')


	"""
	Get directions using google API.
	See documentation at: https://media.readthedocs.org/pdf/python-gmaps/latest/python-gmaps.pdf
	"""
	directions_results = sf.gmaps.directions(origin, 
											destination, 
											mode = "driving", 
											alternatives = True, 
											departure_time = datetime.now())

	#TODO: Make sure the origin and destination are valid, if not loop through 
    #      and try again.

	routes = []
	for directions in directions_results:
		route = []
		steps = sf.getSteps(directions)	

		for step in steps:
			instructions = re.split('<b>', step['html_instructions'])
			
			possible_street = []
			for instruction in instructions:
				parsed_instructions = re.split('</b>', instruction)
				if len(parsed_instructions) == 2:
					possible_street.append(parsed_instructions[0])

			if len(possible_street) >= 1:
				street = sf.getMainStreet(possible_street)
				duration = sf.getDuration(step)
				route.append([street, duration])
				
		routes.append(route)
	
	best_route, route_index = sf.getBestRoute(routes)
	best_route_steps = sf.getSteps(directions_results[route_index])

	sf.printOutput(best_route, best_route_steps, origin, destination)




if __name__ == '__main__':
	main()

