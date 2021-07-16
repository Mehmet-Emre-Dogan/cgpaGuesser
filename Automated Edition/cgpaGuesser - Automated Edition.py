try:
    from msvcrt import getch
    from datetime import date, datetime
    from json import load, dump, loads, dumps
    import tabula
    import pandas as pd
    import ctypes
    from copy import deepcopy

    # You may want to change them
    DEBUG = False
    PRECISION = 3
    #############################

    validLetters = ["AA", "BA", "BB", "CB", "CC", "DC", "DD", "FD", "FF", "NA", "U", "P", "W", "I", "EX", "S"]
    mainMode = -1
    ctypes.windll.kernel32.SetConsoleTitleW("CGPA Oracle")
    print("Loading...")

    pd.set_option("max_columns", None) # Show all rows and coloumns
    pd.set_option("max_rows", None)

    # Funcions

    def isEq(aArr, bArr):
        return sorted(aArr) == sorted(bArr)

    def inputLetter(course, mode="new"):
        while True:
            if mode == "new":
                letter = str(input(f"Please enter your letter guess for course: {course}  --> ")).upper()
            else:
                letter = str(input(f"Please enter your last letter you have (if this is first time, hit enter): {course}  --> ")).upper()
            if letter in validLetters:
                return letter
            elif letter == "" and mode == "old":
                return "--"
            else:
                print(f"Invalid letter: {letter}")

    def letterToGrade(letter):
        if letter == "--":
            return 0
        index = validLetters.index(letter)
        if index>=8 and index<=13:
            return 0
        elif index>= 14 and index<=15:
            return 4
        else:
            return (4 - 0.5*index)

    def selectGuess():
        with open("guessLib.json", "r", encoding="utf-8") as doc:
            guesses = load(doc)
        df2 = pd.DataFrame.from_dict(guesses).T.reset_index().rename(columns={"index":"date"}) # T: transpose
        print(df2[["date"]])
        index = 0
        while True:   
            try:
                index = int(input("Please select the indice you prefer to continue with\n--> "))
                print("="*50)
                return index
            except:
                print("Invalid indice selection!")

    def calcNewWeights(mode = "recent", index = -1):
        with open("guessLib.json", "r", encoding="utf-8") as fil:
            guesses = load(fil)
        gKey = list(guesses.keys())[index]
        lib = deepcopy(guesses[gKey])
        sum = 0
        for course in lib["guessData"]:
            sum += lib["guessData"][course]["weight"]
        if DEBUG:
            print(f"Sum for {gKey}: {sum} ")
        return sum

    def deleteGuess():
        lib = {}
        with open("guessLib.json", "r", encoding="utf-8") as fil:
            lib = load(fil)
        try:
            idx = selectGuess() # select the index of record to be deleted
            key = list(lib.keys())[idx]
            approval = input(f"Indice {key} will be deleted. Type 'yes' to confirm. --> ")
            if approval == 'yes':
                lib.pop(key)
                print(f"{key} deleted successfully.")
                with open("guessLib.json", "w", encoding="utf-8") as doc:
                    dump(lib, doc)
            else:
                print(f"{key} not deleted.")
        except Exception as ex:
            if DEBUG:
                print(ex)
            print("Invaild indice selection. Luckily, nothing was deleted.")

    def guess(mode):
        totalExistingCredit, totalExistingWeight, existingDict, courseCodes, newCreditSum, existingDf = main()
        if DEBUG:
            print("existingDf")
            print(existingDf)
        with open("guessLib.json", "r", encoding="utf-8") as doc:
            guesses = load(doc)
        if mode == "brandNew":
            lib = {"guessData": {}}
            lib.update({"courseArray": courseCodes})
        elif mode == "fromExisting":
            idx = selectGuess()
            gKey = list(guesses.keys())[idx]
            lib = deepcopy(guesses[gKey])
            if not isEq(lib["courseArray"], courseCodes):
                print("This guess is obsolete because it no longer contains the courses in the transcript. Use delete menu if you want to delete.")
                return
        if DEBUG:
            print(existingDict["course_code"])
        for i, course in enumerate(existingDict["course_code"]):
            course = existingDict["course_code"][i]
            credit = existingDict["credit"][i]
            flag = True
            if mode == "fromExisting":
                pref = input(f"--> Saved letter for {course} course is [{lib['guessData'][course]['newletter']}]. Hit enter if you do not want to change.")
                if pref == "":
                    flag = False      
            if flag:
                letter = inputLetter(course, "new")
                oldLetter = inputLetter(course, "old")
                weight = (letterToGrade(letter) - letterToGrade(oldLetter) )*credit
                lib["guessData"].update({ course:{"newletter":letter, "oldletter":oldLetter, "weight":weight } })

        guesses.update({
            str(datetime.now()): lib
        })
        with open("guessLib.json", "w", encoding="utf-8") as doc:
            dump(guesses, doc)

        if DEBUG:
            print(lib["guessData"])
        for course in lib["guessData"]:
            if DEBUG:
                print(course)
            if not lib["guessData"][course]["oldletter"] == "--":
                newCreditSum -= float(existingDf.loc[ existingDf["course_code"] == course, "credit" ])
                if DEBUG:
                    print(f"{course} taken before. So decrease credits as its credit.")
                    print(float(existingDf[ existingDf["course_code"] == course ]["credit"]))

        wei = totalExistingWeight + calcNewWeights()
        cre = totalExistingCredit + newCreditSum                

        drawGuess()
        show(wei, cre)

    def show(wei, cre):
        print("Guessing Results".center(70, "*"))
        print(f"--> Total Credit: {cre} --> Total Prospective Points: {wei}")
        print(f"--> Your Prospective CGPA: {round(float(wei)/float(cre), PRECISION)}")
        print("*"*70)

    def drawGuess(idx = -1):
        with open("guessLib.json", "r", encoding="utf-8") as doc:
            guesses = load(doc)
        key = list(guesses.keys())[idx]
        df = pd.DataFrame.from_dict(guesses[key]["guessData"]).T.reset_index()
        print(" ")
        print(df)
        print(" ")

    def main():
        print("Transcript scraper is running... Please wait")
        transcriptPath = "1.pdf"
        dfArr = tabula.read_pdf(transcriptPath, pages='all', guess=False)

        df = dfArr[0]
        counterDf = dfArr[0]
        currentDf = dfArr[0]

        df.fillna("nanFiller", inplace=True)
        df = df[df.columns[2:4]]
        df = df[df[df.columns[0]].str.contains("CumGPA")]

        df = df.rename(columns={df.columns[0]: "credit",
                                df.columns[1]: "weight"})

        df["credit"] = df["credit"].str.split().str[-1].str.replace(",", ".")
        df.reset_index(inplace=True)
        df.drop(columns="index", inplace=True)
        df["weight"] = df["weight"].str.replace(",", ".")

        df["weight"] = pd.to_numeric(df["weight"], downcast="float")
        df["credit"] = pd.to_numeric(df["credit"], downcast="float")
        if DEBUG:    
            print(df)      
            print("#"*70)
        counterDf = counterDf[counterDf.columns[2:3]]
        counterDf = counterDf[counterDf[counterDf.columns[0]].str.contains("SEM.NO")]
        counterDf = counterDf.rename(columns={counterDf.columns[0]: "semNo"})

        counterDf["semNo"] = counterDf["semNo"].str.split().str[-1]
        semCou = counterDf["semNo"].max()
        if DEBUG:
            print(counterDf)
            print("#"*70)
        firstIdx = counterDf.semNo[counterDf.semNo == semCou].index.tolist()[0]
        if DEBUG:
            print(f"semCou:{semCou} firstIdx:{firstIdx} ")

        currentDf = currentDf[currentDf.columns[2:3]]
        currentDf = currentDf.rename(columns={currentDf.columns[0]: "course_name"})
        endIdx = currentDf.course_name[currentDf.course_name == "nanFiller"].index.tolist()[0]
        currentDf = currentDf[firstIdx+2:endIdx]

        currentDf.reset_index(inplace=True)
        currentDf.drop(columns="index", inplace=True)
        currentDf["course_code"] = currentDf["course_name"].str.split().str[0]
        currentDf["credit"] = currentDf["course_name"].str.split().str[-1].str.replace(",", ".")
        currentDf["course_name"] = currentDf["course_name"].str.split().str[1:-1].str.join(" ")
        currentDf = currentDf[["course_code", "course_name", "credit"]]
        currentDf["credit"] = pd.to_numeric(currentDf["credit"], downcast="float")
        if DEBUG:
            print(currentDf)

        totalExistingCredit = df["credit"].sum()
        totalExistingWeight = df["weight"].sum()
        if DEBUG:
            print('-'*70)
            print(df)
        dictToReturn = currentDf.to_dict()
        courseCodes = currentDf["course_code"].tolist()
        newCreditSum = currentDf["credit"].sum()
        print("="*70)
        print("Transcript scraper have initialized this info, please check whether is true.")
        print(f"Your last credit sum is: {totalExistingCredit}")
        print(f"Your last point sum is: {totalExistingWeight}")
        print(f"Your last CGPA is: {round( ( float(totalExistingWeight)/float(totalExistingCredit) ), PRECISION )} ")
        print(f"You are taking courses worth {newCreditSum} credit for this semester. List of them: ")
        for course in courseCodes:
            print(course)
        print("-"*70)
        return((totalExistingCredit, totalExistingWeight, dictToReturn, courseCodes, newCreditSum, currentDf))

    # main loop
    while mainMode:
        try:
            try:
                mainMode = int(input("1- Make a brand new guess!\n2- Make a guess from existing guess\n3- Show existing guess\n4- Delete existing guess\n0- Exit\n--> "))
            except:
                print("Selection must be an integer!")
            if not ( mainMode >= -1 and mainMode <= 4):
                print("Invalid mode selection!")
                continue

            if mainMode == 1:
                guess("brandNew")
            elif mainMode == 2:
                guess("fromExisting")
            elif mainMode == 3:
                with open("guessLib.json", "r", encoding="utf-8") as doc:
                    guesses = load(doc)
                totalExistingCredit, totalExistingWeight, existingDict, courseCodes, newCreditSum, existingDf  = main()
                idx = selectGuess()
                drawGuess(idx)

                key = list(guesses.keys())[-1]
                lib = guesses[key]
                for course in lib["guessData"]:
                    if DEBUG:
                        print(course)
                    if not lib["guessData"][course]["oldletter"] == "--":
                        newCreditSum -= float(existingDf.loc[ existingDf["course_code"] == course, "credit" ])
                        if DEBUG:
                            print(f"{course} taken before. So decrease credits as its credit.")
                            print(float(existingDf[ existingDf["course_code"] == course ]["credit"]))
                    
                wei = totalExistingWeight + calcNewWeights(idx)
                cre = totalExistingCredit + newCreditSum
                show(wei, cre)

            elif mainMode == 4:
                deleteGuess()
            else:
                pass
            print("="*70)
            
        except (Exception, OSError, RuntimeError, ImportError) as ex:
            print("A small error occured:")
            print(ex)
            print("Press a key to continue app...")
            garbage = getch()

except (Exception, OSError, RuntimeError, ImportError) as ex:
    print("A fatal error occured:")
    print(ex)
    print("Press a key to close app... Then you may want to install some libraries before relaunching the app.")
    garbage = getch()
