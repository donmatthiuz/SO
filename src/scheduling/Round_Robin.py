from src.structure.procesors import *

class RoundRobinScheduler:
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum
        self.processes = []
        self.ready_queue = []
        self.current_time = 0
        
    def add_process(self, procesors):
        
        self.processes = procesors
    
    def get_newly_arrived_processes(self):
        
        newly_arrived = []
        for process in self.processes:
            if (process.arrival_time <= self.current_time and 
                not process.is_completed and 
                process not in self.ready_queue):
                newly_arrived.append(process)
        return newly_arrived
    
    def update_ready_queue(self):
        
        new_arrivals = self.get_newly_arrived_processes()
        self.ready_queue.extend(new_arrivals)
    
    def has_pending_processes(self):
        
        return any(not p.is_completed for p in self.processes)
    
    def advance_to_next_arrival(self):
        
        if not self.ready_queue and self.has_pending_processes():
            next_arrival = min(p.arrival_time for p in self.processes 
                             if not p.is_completed and p.arrival_time > self.current_time)
            self.current_time = next_arrival
    
    def execute_process(self, process):
        
        execution_time = min(self.time_quantum, process.remaining_time)
        
        for _ in range(execution_time):
            process.remaining_time -= 1
            self.current_time += 1
            self.update_ready_queue()
        
        if process.remaining_time == 0:
            process.is_completed = True
            process.completion_time = self.current_time
            return True
        return False
    
    def calculate_metrics(self):
        for process in self.processes:
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
    
    def run_scheduler(self):
        self.current_time = min(p.arrival_time for p in self.processes)
        self.update_ready_queue()
        
        while self.has_pending_processes():
            if not self.ready_queue:
                self.advance_to_next_arrival()
                self.update_ready_queue()
                continue
            
            current_process = self.ready_queue.pop(0)
            process_completed = self.execute_process(current_process)
            
            # Si el proceso no se completó, regresarlo a la cola
            if not process_completed:
                self.ready_queue.append(current_process)
        
        self.calculate_metrics()
    
    def display_results(self):
        """Muestra los resultados del algoritmo"""
        print("\nProcess ID\tArrival Time\tBurst Time\tWaiting Time\tTurnaround Time")
        print("-" * 75)
        
        total_waiting = 0
        total_turnaround = 0
        
        for process in self.processes:
            print(f"{process.pid}\t\t{process.arrival_time}\t\t{process.burst_time}\t\t"
                  f"{process.waiting_time}\t\t{process.turnaround_time}")
            total_waiting += process.waiting_time
            total_turnaround += process.turnaround_time
        
        avg_waiting = total_waiting / len(self.processes)
        avg_turnaround = total_turnaround / len(self.processes)
        
        print(f"\nAverage Waiting Time: {avg_waiting:.2f}")
        print(f"Average Turnaround Time: {avg_turnaround:.2f}")

def get_user_input():
    """Obtiene la entrada del usuario"""
    print("=== Round Robin Process Scheduler ===")
    
    time_quantum = int(input("\nEnter time quantum: "))
    
    scheduler = RoundRobinScheduler(time_quantum)
    
    return scheduler

def main():
    """Función principal"""
    try:
        scheduler = get_user_input()
        procesors = cargar_procesos_desde_archivo('./data/procesors.txt')
        scheduler.add_process(procesors)
        
        print("\nExecuting Round Robin Algorithm...")
        scheduler.run_scheduler()
        
        print("\n" + "="*50)
        print("SCHEDULING RESULTS")
        print("="*50)
        scheduler.display_results()
        
    except ValueError:
        print("Error: Please enter valid integer values.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()