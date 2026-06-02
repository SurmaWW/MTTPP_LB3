import threading
import random
import time

NUM_ACCOUNTS = 167   # Створюємо 167 рахунків
NUM_THREADS = 1167   # Запускаємо 1167 потоків
RUN_TIME = 2         # Скільки секунд триватиме симуляція

# Ініціалізація рахунків випадковими сумами від 100 до 1000
accounts = [random.randint(100, 1000) for _ in range(NUM_ACCOUNTS)]
account_locks = [threading.Lock() for _ in range(NUM_ACCOUNTS)]

initial_sum = sum(accounts)
print(f"Старт дефектної симуляції")
print(f"Початкова сума грошей {initial_sum} грн\n")

stop_signal = False

# 1. ФУНКЦІЯ З RACE CONDITION 
def race_condition_worker():
    global stop_signal
    while not stop_signal:
        from_acc = random.randint(0, NUM_ACCOUNTS - 1)
        to_acc = random.randint(0, NUM_ACCOUNTS - 1)
        if from_acc == to_acc:
            continue
            
        amount = random.randint(1, 10)
        
        if accounts[from_acc] >= amount:
            current_from = accounts[from_acc]
            time.sleep(0.000001) 
            accounts[from_acc] = current_from - amount
            
            current_to = accounts[to_acc]
            time.sleep(0.000001)
            accounts[to_acc] = current_to + amount

# 2. ФУНКЦІЯ З DEADLOCK 
def deadlock_worker():
    global stop_signal
    while not stop_signal:
        from_acc = random.randint(0, NUM_ACCOUNTS - 1)
        to_acc = random.randint(0, NUM_ACCOUNTS - 1)
        if from_acc == to_acc:
            continue
            
        amount = random.randint(1, 10)
        
        account_locks[from_acc].acquire()
        time.sleep(0.0001)
        account_locks[to_acc].acquire()
        
        if accounts[from_acc] >= amount:
            accounts[from_acc] -= amount
            accounts[to_acc] += amount
            
        account_locks[to_acc].release()
        account_locks[from_acc].release()

# Тест 1: Демонстрація Race Condition
print("Запуск потоків Race Condition...")
threads = []
for _ in range(NUM_THREADS):
    t = threading.Thread(target=race_condition_worker)
    threads.append(t)
    t.start()

time.sleep(RUN_TIME)
stop_signal = True

for t in threads:
    t.join()

final_sum_race = sum(accounts)
print(f"Загальна сума в кінці {final_sum_race} грн")
print(f"Втрачено грошей {final_sum_race - initial_sum} грн\n")

# Тест 2: Демонстрація Deadlock
stop_signal = False
accounts = [random.randint(100, 1000) for _ in range(NUM_ACCOUNTS)]
print("Запуск потоків для демонстрації Deadlock...")
deadlock_threads = []

for _ in range(NUM_THREADS):
    t = threading.Thread(target=deadlock_worker)
    deadlock_threads.append(t)
    t.start()

print("Програма зависає через Deadlock. Ждемо 20 секунд і вимикаємо програму")
time.sleep(20)
import os
os._exit(0)