#Variabelen: 
data <- readFromUSB
avg_list <- list()
raw_list <- queue()
raw_avg <- double()
avg_of_avg <- double()
diff <- double()
prev_state <- state()
new_state <- state()
#Algoritme:
if(len(raw_list) < 5):
	#raw_list opvullen tot lengte 5 
	raw_list.append(data)
else:
	#Als raw_list lengte 5 heeft: linkse shift toepassen
	raw_list.popleft()
	raw_list.append(data)
	#Bereken het gemiddelde van de raw_list -> raw_avg
	raw_avg = avg(raw_list)
	#Voeg toe aan de avg_list en bereken avg_of_avg
	avg_list.append(raw_avg)
	avg_of_avg = avg(avg_list)
	#Bereken het verschil tussen het raw_avg en de avg_of_avg
	diff = raw_avg - avg_of_avg
	#Bereken nieuwe toestand op basis van voorgaande state en diff
	new_state = calc_state(prev_state, diff)
	#Als de nieuwe toestand verschilt van de oude:
		#Maak de lijsten leeg zodat nieuwe gemiddeldes kunnen 
		#berekent worden voor de nieuwe toestand.
	if(new_state != prev_state):
		avg_list.clear()
		raw_list.clear()
		prev_state = new_state
	run_state(new_state)