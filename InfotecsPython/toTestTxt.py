import re # for regulars


# Same class lies in script.py
class workerTxt:
    def __init__(self, filename):
        self.filename = filename
    def get_town_by_id(self, id):
        file = open(self.filename)
        for line in file:
            if(line.startswith(str(id)+'\t')):
                return line.replace(str(id)+'\t', '')
        return "No such town"
    def get_n_towns_from(self, id, count):
        file = open(self.filename)
        towns = []
        n = 0
        start_count = False
        for line in file:
            if(line.startswith(str(id)+'\t')):
                start_count = True
            if(start_count):
                if(n == count):
                    return towns
                towns.append(re.sub(r'^\d*\t','',line))
                n += 1
        if(not start_count):
            return "No such town"
        file = open(self.filename)
        for line in file:
            if (n == count):
                return towns
            towns.append(re.sub(r'^\d*\t','',line))
            n += 1
    def get_n_towns(self, count):
        file = open(self.filename)
        towns = []
        for i in range(count):
            towns.append(re.sub(r'^\d*\t','',file.readline()))
        return towns
    def get_norther_town(self, first, second):
        file = open(self.filename)
        first_pretenders = [] # номинанты быть первым городом
        second_pretenders = [] # номинанты быть вторым городом
        for line in file:
            info = line.split('\t')
            search = re.search("," + first + r"$", info[3])
            if(search): # состоит ли первый город в перечислении альтернативных названий города
                first_pretenders.append(info)
            search = re.search("," + second + r"$", info[3])
            if(search):
                second_pretenders.append((info))
        if(not first_pretenders and not second_pretenders):
            return "No such towns"
        if(not first_pretenders):
            return "No such first town"
        if(not second_pretenders):
            return "No such second town"
        if(len(first_pretenders)>1):
            nice_pretender = first_pretenders[0]
            for pretender in first_pretenders: # Рассматриваем каждого претендента
                if(pretender[14]>nice_pretender[14]):
                    nice_pretender = pretender
            first_pretenders = [nice_pretender]
        if(len(second_pretenders)>1):
            nice_pretender = second_pretenders[0]
            for pretender in second_pretenders:  # Рассматриваем каждого претендента
                if (pretender[14] > nice_pretender[14]):
                    nice_pretender = pretender
            second_pretenders = [nice_pretender]
        if(first_pretenders[0][4] >= second_pretenders[0][4]):
            town1 = "\t".join(first_pretenders[0][1:])
            town2 = "\t".join(second_pretenders[0][1:])
        if(second_pretenders[0][4] > first_pretenders[0][4]):
            town1 = "\t".join(second_pretenders[0][1:])
            town2 = "\t".join(first_pretenders[0][1:])
        difference = "Нет временной разницы" if first_pretenders[0][-2] == second_pretenders[0][-2] else "Есть временная разница"
        towns = {"north":town1,"south":town2,"difference":difference}
        return towns




# TESTS
if(__name__ == "__main__"):
    worker = workerTxt("RU.txt")
    # print("No such town (id == 1):\n", worker.get_town_by_id(1))
    # print("Return town:\n", worker.get_town_by_id(451748))
    test = worker.get_n_towns_from(451747,50)
    print("Return 50 towns:\n", test)
    test = worker.get_n_towns_from(12110389,50)
    print(f"Return 50 towns after end of file:\n Length == {len(test)}\n", test[0],test[49])
    print("No such town (id == 1):\n", worker.get_n_towns_from(1,50))
    # print("Return 50 towns from start:\n", worker.get_n_towns(50))
    # print("No such towns:\n", worker.get_norther_town("asd","asdsf"))
    # print("Return norther town, no difference:\n", worker.get_norther_town("Посёлок Логи","Гора Петяявара"))
    # print("Return norther town, there is difference:\n", worker.get_norther_town("Урочище Салокачи", "Гора Петяявара"))