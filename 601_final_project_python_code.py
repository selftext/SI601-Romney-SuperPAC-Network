# The following code creates a list for exploring the network of relationships between donors to Mitt Romney's SuperPAC 'Restore Our Future'
# Written by Paul Ellebrecht, Lettie Malan, Nikki Roda, Jeremy Salfen, Phillip Tularak for SI601 at University of Michigan in Winter 2012

import urllib
import xml.etree.ElementTree as ET

#query LittleSis for xml output showing all donors to Romney's SuperPAC
url = 'http://api.littlesis.org/entity/69678/relationships.xml?cat_id=5&_key=1b0a067953d4285315ec6e45d0ea9960af6e9933'

document = urllib.urlopen(url)
tree = ET.parse(document)
doc = tree.getroot()

#create dictionary to store Romney donors and amount donated
donors = {}

#create dictionary to store all donors as nodes
entityDict = {}

#create list to store all edge relationships
edgeList = []

#create list to store entity2_ids
entity2List = []

#loop through the xml output and store in the donors dictionary the following: 
#entity ID of the donor as key, the amount donated as value
for entity in doc.findall('Data/Relationships/Relationship'):
    #skip if the relationship is not a donation
    if entity.find('category_id').text != '5' : continue
    donors[entity.find('entity1_id').text] = entity.find('amount').text

count = 0

#loop through the Romney donors to pull out who else they donated to and how much
for key in donors:
    #get xml output for each Romney donor
    url = 'http://api.littlesis.org/entity/' + key + '/relationships.xml?cat_id=5&_key=1b0a067953d4285315ec6e45d0ea9960af6e9933'
    document = urllib.urlopen(url)
    tree = ET.parse(document)
    doc = tree.getroot()
    #add Romney donor to the nodes dictionary using the following:
    #entity ID of the donor as key, name and description of the donor as the value (in a tuple)
    for entityKey in doc.findall('Data/Entity'):
        #clean for guess input - replace commas with dashes
        name = entityKey.find('name').text
        name = name.replace(',',' - ')
        desc = entityKey.find('description').text
        if desc != None:
            desc = desc.replace(',',' - ')
        entityDict[key] = (name, desc)
    #find all other donations that the Romney donor made
    for entity in doc.findall('Data/Relationships/Relationship'):
        #skip if the relationship is not donation
        if entity.find('category_id').text != '5' : continue
        #some donations are old, so skip donations made before 2008
        date = entity.find('end_date').text
        if date != None:          
            #find year of donation
            year = date.split('-')[0]
            #only pull data after 2008
            if int(year) < 2008 : continue
        #skip if the amount of donation is empty
        if entity.find('amount').text == None: continue
        #store edge in list as tuple with the following:
        #entity ID of Romney donor, entity ID of who Romney donor donated to, amount of donation
        entity2 = entity.find('entity2_id').text
        edge = (key, entity2, entity.find('amount').text)
        edgeList.append(edge)
        #add entity2_ids to list so we can add them to the nodes dictionary later
        entity2List.append(entity2)
    count = count + 1
    print count

#confirmation that all Romney donors have been added to the nodes dictionary
#and that all donations have been added to the edges dictionary
print 'success 1'

newCount = 0

#get names and descriptions for all the other entities the Romney donors donated to
for x in entity2List:
    #skip if donor is already in the nodes dictionary
    if x not in entityDict:
        #get xml output for entity
        url = 'http://api.littlesis.org/entity/' + x + '/relationships.xml?cat_id=5&_key=1b0a067953d4285315ec6e45d0ea9960af6e9933'
        document = urllib.urlopen(url)
        tree = ET.parse(document)
        doc = tree.getroot()
        #add entity to the node dictionary with the following:
        #entity ID of the donor as key, name and description of the donor as the value (in a tuple)
        for entityKey in doc.findall('Data/Entity'):
            #clean for guess input - replace commas with dashes
            name = entityKey.find('name').text
            name = name.replace(',',' - ')
            desc = entityKey.find('description').text
            if desc != None:
                desc = desc.replace(',',' - ')
            entityDict[x] = (name,desc)
    newCount = newCount + 1
    print newCount

#confirmation that the nodes dictionary is complete
print 'success 2'

#open file to write data
OUT = open('littlesis_data.txt', 'w')

#write first line for nodes
OUT.write('nodedef>name VARCHAR,label VARCHAR,description VARCHAR\n')

#print nodes to file
for key in entityDict:
    #add 'a' to beginning of IDs to format for guess input (which doesn't like nodes to start with numbers)
    OUT.write('a' + str(key) + ',' + str(entityDict[key][0]) + ',' + str(entityDict[key][1])+'\n')

#write first line for edges
OUT.write('\n\nedgedef>node1 VARCHAR,node2 VARCHAR,directed BOOLEAN,weight INT\n')

#print edges to file
i = 0
for x in edgeList:
    #add 'a' to beginning of IDs, add true to indicate direction
    OUT.write('a' + str(edgeList[i][0]) + ',' + 'a' + str(edgeList[i][1]) + ',' 'true' + ',' + str(edgeList[i][2]) + '\n')
    i = i + 1

#confirmation that writing to file is complete
print 'success 3'

OUT.close()