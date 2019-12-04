def check_pw(password):
    password = str(password)
    #if not len(password)==6:
    #    return false
    if password[0] == password[1] or password[1] == password[2] or password[2] == password[3] or password[3] == password[4] or password[4] == password[5]:
        pass
    else:
        return False
    
    last_digit = 0
    for i in range(len(password)):
        if password[i]>=last_digit:
            last_digit = password[i]
        else:
            return False
    return True

def check_pw_part2(password):
    password = str(password)
    if password[0] == password[1] != password[2] or password[0] != password[1] == password[2] != password[3] or password[1] != password[2] == password[3] != password[4] or password[2] != password[3] == password[4] != password [5] or password[3] != password[4] == password[5]:
        pass
    else:
        return False
    return True

result = []
for p in range(183564,657474+1):
    result.append(check_pw(p))

print("Part 1: ",result.count(True))

result = []
for p in range(183564,657474+1):
    result.append(check_pw(p) and check_pw_part2(p))
print("Part 2: ",result.count(True))
