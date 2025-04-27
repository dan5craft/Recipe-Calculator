import math
import json
import sys
sys.setrecursionlimit(5000)

loop = True
while loop:
    jsonFileName = input("Name of json file: ")+".json"
    try:
        with open(jsonFileName) as f:
            items = json.load(f)
            loop = False
            print(jsonFileName+" Was found")
    except:
        print(jsonFileName+" does not exist")
        confirm = input("Do you want to create it? y/n ")
        if confirm.lower() == "y":
            with open(jsonFileName, "w") as f:
                items = {
                    "stockedItems": [],
                    "itemList": []
                }
                json.dump(items, f, indent=2)
                print(jsonFileName+" Created")
            with open(jsonFileName) as f:
                items = json.load(f)
                loop = False
rawItems = []
rawAmounts = []
combinedItems = []
combinedAmounts = []
dependants = []

class Item:
    def __init__(self, name, count):
        self.name = name
        self.count = count

def findItemInList(name, list):
    for item in list:
        if item.name.lower() == name.lower():
            return list.index(item)
    return -1

def printItemList():
    print("List of all items\nName | ID")
    for x in items["itemList"]:
        print(x["name"]+" #"+str(x["id"]))

def printRecipeList():
    print("List of all recipes\nName | ID")
    for x in items["itemList"]:
        if x["recipeItemIds"] != []:
            print(x["name"]+" #"+str(x["id"]))

def inItemList(name="", id=-1):
    for x in items["itemList"]:
        if x["id"] == id or x["name"].lower() == name.lower():
            return True
    return False

def inStockedItems(id=-1):
    for x in items["stockedItems"]:
        if x == id:
            return True
    return False

def getItemFromId(id):
    for x in items["itemList"]:
        if x["id"] == id:
            return x
    print("Could not find item with id "+str(id)+", Please add it.")
    return None

def getItemFromName(name):
    for x in items["itemList"]:
        if x["name"].lower() == name.lower():
            return x
    print("Could not find item with name "+name+", Please add it.")
    return None

def addItem(name="Undefined", id=-1, recipeItemIds=[], recipeItemAmounts=[], recipeYield=1):
    if not inItemList(name, id):
        itemDict = {
            "name": name,
            "id": id,
            "recipeItemIds": recipeItemIds,
            "recipeItemAmounts": recipeItemAmounts,
            "recipeYield": recipeYield
        }
        items["itemList"].append(itemDict)
        with open(jsonFileName, "w") as f:
            json.dump(items, f, indent=2)
    else:
        print("That item already exists!")

def editItem(item, changedName, recipeItemIds=[], recipeItemAmounts=[], recipeYield=1):
    item["name"] = changedName
    item["recipeItemIds"] = recipeItemIds
    item["recipeItemAmounts"] = recipeItemAmounts
    item["recipeYield"] = recipeYield
    with open(jsonFileName, "w") as f:
        json.dump(items, f, indent=2)

def calculateRecipe(item, amount, layer=0, leftovers=[]):
    if findItemInList(item["name"], leftovers) != -1:
        diff = amount - leftovers[findItemInList(item["name"], leftovers)].count
        if(diff < 1):
            leftovers[findItemInList(item["name"], leftovers)].count -= amount
            return
        else:
            amount -= leftovers[findItemInList(item["name"], leftovers)].count
            leftovers.pop(findItemInList(item["name"], leftovers))
    recipeCount = math.ceil(amount/item["recipeYield"])
    itemIds = item["recipeItemIds"]
    if inStockedItems(item["id"]) and layer > 0:
        itemIds = []
        actualAmount = amount
    else:
        actualAmount = item["recipeYield"]*recipeCount
    if(actualAmount > amount):
        if findItemInList(item["name"], leftovers) == -1:
            leftovers.append(Item(item["name"],actualAmount-amount))
        else:
            leftovers[findItemInList(item["name"], leftovers)].count += actualAmount-amount
    for x in range(len(itemIds)):
        calculateRecipe(getItemFromId(itemIds[x]), item["recipeItemAmounts"][x]*recipeCount, layer+1,leftovers)
    if itemIds == []:
        if rawItems.count(item) == 0:
            rawItems.append(item)
            rawAmounts.append(actualAmount)
        else:
            rawAmounts[rawItems.index(item)] += actualAmount
    if combinedItems.count(item) == 0:
        combinedItems.append(item)
        combinedAmounts.append(actualAmount)
        if layer == 1:
            combinedItems.append("")
            combinedAmounts.append("")
    else:
        combinedAmounts[combinedItems.index(item)] += actualAmount
    if layer == 0:
        leftovers.clear()
        print("\n# How to craft "+str(amount)+" "+item["name"]+".\n")
        print("## Raw materials required:")
        for x in range(len(rawItems)):
            print("- "+str(rawAmounts[x])+" "+rawItems[x]["name"])
        print("\n## Combined amounts:")
        for x in range(len(combinedItems)):
            if combinedItems[x] == "":
                print("")
            elif rawItems.count(combinedItems[x]) > 0:
                print("- get "+str(combinedAmounts[x])+" "+combinedItems[x]["name"])
            else:
                print("- craft "+str(combinedAmounts[x])+" "+combinedItems[x]["name"])

def addItems():
    item = input("\nitem name:\n")
    if item == "":
        menu()
        return
    if inItemList(item):
        print("That item is already added")
        addItems()
        return
    print()
    printItemList()
    recipeItems = input("\nitems required to make "+item+":\nleave blank if "+item+" has no recipe\n")
    recipeItemAmounts = []
    recipeYield = ""
    if recipeItems != "":
        recipeItems = recipeItems.split(", ")
        error = False
        actualRecipeItems = []
        for x in recipeItems:
            if x.isdigit():
                recipeItem = getItemFromId(int(x))
                if(recipeItem == None):
                    error = True
            else:
                recipeItem = getItemFromName(x)
                if(recipeItem == None):
                    error = True
            if(recipeItem != None):
                actualRecipeItems.append(recipeItem["id"])
        if error:
            print("please start over:")
            addItems()
            return
        recipeItems = actualRecipeItems
        print("Item amounts")
        recipeString = ""
        for x in recipeItems:
            amount = ""
            while not amount.isdigit() or amount.isdigit() and int(amount) < 1:
                amount = input(getItemFromId(x)["name"]+" ")
            recipeItemAmounts.append(int(amount))
            recipeString += amount+" "+getItemFromId(x)["name"]+"\n"
        while not recipeYield.isdigit() or recipeYield.isdigit and int(recipeYield) < 1:
            recipeYield = input("the amount of "+item+" you get from the recipe:\n")
        confirm = input("Confirm item "+item+"\nRecipe for "+recipeYield+" "+item+":\n"+recipeString+"y/n: ")
    else:
        recipeItems = []
        recipeYield = 1
        confirm = input("Confirm item "+item+"\n(no recipe)\ny/n: ")
    if confirm.lower() == "y":
        addItem(item, len(items["itemList"]), recipeItems, recipeItemAmounts, int(recipeYield))
        print("added item.")
    reset = input("Want to go to the menu? y/n: ")
    if reset.lower() == "y":
        menu()
        return
    else:
        addItems()
        return

def editItems():
    printItemList()
    item = input("\nitem to edit:\n")
    if item == "":
        menu()
        return
    if item.isdigit():
        if not inItemList("", int(item)):
            print("can't find item with id "+item)
            editItems()
            return
        item = getItemFromId(int(item))
    else:
        if not inItemList(item):
            print("can't find item with name "+item)
            editItems()
            return
        item = getItemFromName(item)
    recipeString = ""
    if item["recipeItemIds"] != []:
        for x in range(len(item["recipeItemIds"])):
            recipeString += str(str(item["recipeItemAmounts"][x]))+" "+getItemFromId(item["recipeItemIds"][x])["name"]+"\n"
        print("Current state of "+item["name"]+"\nRecipe for "+str(item["recipeYield"])+" "+item["name"]+":\n"+recipeString)
    else:
        print("Current state of "+item["name"]+"\n(no recipe)")
    changedName = input("New name for "+item["name"]+":\n")
    if(changedName == ""):
        print("Keeping name "+item["name"])
        changedName = item["name"]
    recipeItems = input("\nitems required to make "+changedName+":\nleave blank if "+changedName+" has no recipe\n")
    recipeItemAmounts = []
    recipeYield = ""
    if recipeItems != "":
        recipeItems = recipeItems.split(", ")
        error = False
        actualRecipeItems = []
        for x in recipeItems:
            if x.isdigit():
                recipeItem = getItemFromId(int(x))
                if(recipeItem == None):
                    error = True
            else:
                recipeItem = getItemFromName(x)
                if(recipeItem == None):
                    error = True
            if(recipeItem != None):
                actualRecipeItems.append(recipeItem["id"])
        if error:
            print("please start over:")
            editItems()
            return
        recipeItems = actualRecipeItems
        print("Item amounts:")
        recipeString = ""
        for x in recipeItems:
            amount = ""
            while not amount.isdigit() or amount.isdigit() and int(amount) < 1:
                amount = input(getItemFromId(x)["name"]+" ")
            recipeItemAmounts.append(int(amount))
            recipeString += amount+" "+getItemFromId(x)["name"]+"\n"
        while not recipeYield.isdigit() or recipeYield.isdigit and int(recipeYield) < 1:
            recipeYield = input("the amount of "+changedName+" you get from the recipe:\n")
        confirm = input("Confirm edit of "+item["name"]+"\nNew name: "+changedName+"\nRecipe for "+recipeYield+" "+changedName+":\n"+recipeString+"y/n: ")
    else:
        recipeItems = []
        recipeYield = 1
        confirm = input("Confirm edit of "+item["name"]+"\nNew name: "+changedName+"\n(no recipe)\ny/n: ")
    if confirm.lower() == "y":
        editItem(item, changedName, recipeItems, recipeItemAmounts, int(recipeYield))
        print("edited item.")
    else:
        print("did not edit item")
    reset = input("Want to go to the menu? y/n: ")
    if reset.lower() == "y":
        menu()
        return
    else:
        editItems()
        return

def calculateRecipes():
    print()
    printRecipeList()
    recipe = input("\nRecipe to calculate:\n")
    if recipe == "":
        menu()
        return
    if recipe.isdigit():
        if not inItemList("", int(recipe)):
            print("can't find item with id "+recipe)
            calculateRecipes()
            return
        recipe = getItemFromId(int(recipe))
    else:
        if not inItemList(recipe):
            print("can't find item with name "+recipe)
            calculateRecipes()
            return
        recipe = getItemFromName(recipe)
    if recipe["recipeItemIds"] == []:
        print("That item doesn't have a recipe")
        calculateRecipes()
        return
    amount = ""
    while not amount.isdigit() or amount.isdigit() and int(amount) < 1:
        amount = input("Amount to craft:\n")
    combinedItems.clear()
    combinedAmounts.clear()
    rawItems.clear()
    rawAmounts.clear()
    calculateRecipe(recipe, int(amount))
    reset = input("\nWant to go to the menu? y/n: ")
    if reset.lower() == "y":
        menu()
        return
    else:
        calculateRecipes()
        return

def stockedString():
    string = ""
    for x in range(len(items["stockedItems"])):
        if x < len(items["stockedItems"])-1:
            string += getItemFromId(items["stockedItems"][x])["name"]+", "
        else:
            string += getItemFromId(items["stockedItems"][x])["name"]
    return string

def changeStockedItems():
    print()
    printItemList()
    if stockedString() == "":
        print("\nCurrently stocked items is empty.\n")
    else:
        print("\nCurrently stocked items:\n"+stockedString()+"\n")
    stockedItems = input("Stocked items:\ntype \"current\" to get current stocked items.\n")
    if stockedItems != "":
        stockedItems = stockedItems.split(", ")
        stockedIds = []
        error = False
        for stock in stockedItems:
            if stock.lower() == "current":
                for sock in items["stockedItems"]:
                    stockedIds.append(sock)
            else:
                if stock.isdigit():
                    if inItemList("", int(stock)):
                        stockedIds.append(int(stock))
                    else:
                        print("can't find item with id "+stock)
                        error = True
                else:
                    if inItemList(stock):
                        stockedIds.append(getItemFromName(stock)["id"])
                    else:
                        print("can't find item with name "+stock)
                        error = True
        if error:
            print("please try again.")
            changeStockedItems()
            return
        print("Changed stocked items")
    else:
        stockedIds = []
        print("Cleared stocked items.")
    items["stockedItems"] = stockedIds
    with open(jsonFileName, "w") as f:
        json.dump(items, f, indent=2)
    reset = input("Want to go to the menu? y/n: ")
    if reset.lower() == "y":
        menu()
        return
    else:
        changeStockedItems()
        return

def findDependants(item):
    for x in items["itemList"]:
        for y in x["recipeItemIds"]:
            if item["id"] == y:
                if(dependants.count(x) == 0):
                    dependants.append(x)
                    findDependants(x)

def deleteItems():
    print()
    printItemList()
    item = input("\nItem to delete:\n")
    if item == "":
        menu()
        return
    if item.isdigit():
        if not inItemList("", int(item)):
            print("can't find item with id "+item)
            deleteItems()
            return
        item = getItemFromId(int(item))
    else:
        if not inItemList(item):
            print("can't find item with name "+item)
            deleteItems()
            return
        item = getItemFromName(item)
    dependants.clear()
    findDependants(item)
    confirm = ""
    if dependants == []:
        confirm = input("\nAre you sure you want to delete "+item["name"]+".\ny/n: ")
    else:
        print("\nThis item has "+str(len(dependants))+" dependants:")
        for x in dependants:
            print(x["name"])
        print("\nYou have to delete or edit these items before you can delete this one.")
    if confirm == "y":
        print("Deleted "+item["name"]+".")
        items["itemList"].remove(item)
        with open(jsonFileName, "w") as f:
            json.dump(items, f, indent=2)
    reset = input("\nWant to go to the menu? y/n: ")
    if reset.lower() == "y":
        menu()
        return
    else:
        deleteItems()
        return

def sortItems():
    confirm = input("\nAre you sure you want to sort all items in alphabetical order?\ny/n ")
    if confirm.lower() != "y":
        menu()
        return
    names = []
    for x in items["itemList"]:
        names.append(x["name"].lower())
    names.sort()
    newItemList = []
    for x in names:
        newItemList.append(getItemFromName(x).copy())
    for x in newItemList:
        x["id"] = names.index(x["name"].lower())
        for y in range(len(x["recipeItemIds"])):
            x["recipeItemIds"][y] = names.index(getItemFromId(x["recipeItemIds"][y])["name"].lower())
    stockItems = []
    for x in range(len(items["stockedItems"])):
        stockItems.append(names.index(getItemFromId(items["stockedItems"][x])["name"].lower()))
    items["stockedItems"] = stockItems
    items["itemList"] = newItemList
    with open(jsonFileName, "w") as f:
        json.dump(items, f, indent=2)
    print("Item list sorted")
    printItemList()
    menu()

def menu():
    mode = input("\nMode select:\n1. add items | 2. edit items | 3. calculate recipes\n4. change stocked items | 5. DELETE items | 6. sort items\n")
    if mode == "1" or mode.lower() == "add items":
        addItems()
    elif mode == "2" or mode.lower() == "edit items":
        editItems()
    elif mode == "3" or mode.lower() == "calculate recipes":
        calculateRecipes()
    elif mode == "4" or mode.lower() == "change stocked items":
        changeStockedItems()
    elif mode == "5" or mode.lower() == "delete items":
        deleteItems()
    elif mode == "6" or mode.lower() == "sort items":
        sortItems()
    else:
        print("Invalid input")
        menu()
print()
printItemList()
print("\nWelcome to Recipe calculator 2.0!")
menu()
