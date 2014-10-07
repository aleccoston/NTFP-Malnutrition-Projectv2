import ast
"""
takes list of patients who could not be matched to a city, probably
because the city was misspelled. compares to a growing list of common
misspellings to find a match

"""

def catchSpellings(city_dict,unMatchedList,totalPatients):
    #note: consolidate paths
    dictOfSpellings={}
    newUnMatchedList=[]
    file=open('/Users/Alec_/pythonMods/altSpellingListv2.txt')
    #make dict of misspellings from lines in file=dictOfSpellings
    for line in file.read().splitlines():
        key=ast.literal_eval(line.split(':')[0]) 
        listS=ast.literal_eval(line.split(':')[1])
        dictOfSpellings[key]=listS
    file.close()
    
    
    #go through unmatched list searching for match in list of common mispels
    while len(unMatchedList)>0:
        currentPatient=unMatchedList.pop()
        foundMatch=False
        for [cityName,mispelList] in dictOfSpellings.iteritems():
            #cycle through each city and its spellings to find match
            for spelling in mispelList:
                if spelling.lower() in currentPatient.lower():
                    #print 'found a match!'
                    foundMatch=True
                    #add patient to malnutrition data structure
                    if 'malnutritionsevere' in currentPatient.lower():
                            
                            city_dict[cityName][2]+=1
                    elif 'malnutritionmoderate' in currentPatient.lower():
                            city_dict[cityName][1]+=1
                    elif 'malnutritionmild' in currentPatient.lower():
                            city_dict[cityName][0]+=1
                    else:
                            pass #note: throw an error, bad query
                if foundMatch:
                    break #out of misSpelList for loop
            if foundMatch:
                break #out of city search for this patient
            
        if not foundMatch:
            #catches patients still unmatched
            newUnMatchedList.append(currentPatient) 

    print '%.0f%% of patients unmatched' %(float(len(newUnMatchedList))/totalPatients*100)
    return [city_dict,newUnMatchedList]
    

def containsCity(cityName,patientInfo):
    #note: consolidate paths
    dictOfSpellings={}
    
    file=open('/Users/Alec_/pythonMods/altSpellingListv2.txt')
    #make dict of misspellings from lines in file=dictOfSpellings
    for line in file.read().splitlines():
        key=ast.literal_eval(line.split(':')[0]) 
        listS=ast.literal_eval(line.split(':')[1])
        dictOfSpellings[key]=listS
    file.close()
    isaMatch=False
    if dictOfSpellings.has_key(cityName):
        
        spellingList=dictOfSpellings[cityName]
    else:
        return False
    for city in spellingList:
        if city.lower() in patientInfo.lower():
            isaMatch=True

    return isaMatch
    
    
                        
        
