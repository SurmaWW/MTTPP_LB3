import threading
import random
import time

NUM_ACCOUNTS = 167
NUM_THREADS = 4096
RUN_TIME = 2

accounts = [random.randint(100, 1000) for _ in range(NUM_ACCOUNTS)]
# Створюємо замки для кожного рахунку
account_locks = [threading.Lock() for _ in range(NUM_ACCOUNTS)]

initial_sum = sum(accounts)
print(f"Загальна сума грошей {initial_sum} грн\n")

stop_signal = False

def safe_fixed_worker():
    global stop_signal
    while not stop_signal:
        from_acc = random.randint(0, NUM_ACCOUNTS - 1)
        to_acc = random.randint(0, NUM_ACCOUNTS - 1)
        if from_acc == to_acc:
            continue
            
        amount = random.randint(1, 10)

        first_lock = min(from_acc, to_acc)
        second_lock = max(from_acc, to_acc)
        

        with account_locks[first_lock]:
            with account_locks[second_lock]:
                if accounts[from_acc] >= amount:
                    accounts[from_acc] -= amount
                    accounts[to_acc] += amount

start_perf = time.perf_counter()
threads = []
for _ in range(NUM_THREADS):
    t = threading.Thread(target=safe_fixed_worker)
    threads.append(t)
    t.start()

time.sleep(RUN_TIME)
stop_signal = True

for t in threads:
    t.join()

end_perf = time.perf_counter()
final_sum = sum(accounts)

print(f"Загальна сума грошей в кінці {final_sum} грн")
print(f"Різниця {final_sum - initial_sum} грн")
print(f"Час виконання симуляції: {end_perf - start_perf:.4f} секунд.")