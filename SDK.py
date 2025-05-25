import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
from typing import List, Optional, Tuple
from copy import deepcopy
from heapq import heappush, heappop
import tracemalloc
import gc
import sys
import argparse

# ================= PHẦN THUẬT TOÁN =================
class SudokuSolver:
    def __init__(self, board: Optional[List[List[int]]] = None):
        self.board = board or [[0]*9 for _ in range(9)]
        self.initial_board = deepcopy(self.board)
        self.empty_cells = []  # Danh sách (num_options, row, col) cho MRV
        self.all_puzzles = {
            'easy': [
        # 32 ô đã điền, 49 ô trống - Tăng độ khó một chút so với ban đầu
       [[9, 0, 0, 3, 1, 0, 0, 0, 4],
        [0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 0, 0, 5, 6, 8, 0, 9],
        [0, 2, 4, 6, 8, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 3, 0, 0, 1],
        [6, 3, 0, 0, 0, 0, 4, 0, 0],
        [0, 0, 8, 0, 0, 0, 1, 5, 0],
        [2, 9, 1, 0, 6, 4, 7, 3, 0],
        [5, 6, 0, 1, 7, 8, 9, 4, 0]]
    ],
            'medium': [
        # 28 ô đã điền, 53 ô trống - Giảm độ khó so với hiện tại
       [[0, 0, 0, 0, 0, 0, 0, 0, 5],
        [0, 0, 0, 2, 8, 5, 7, 1, 3],
        [8, 0, 5, 0, 0, 0, 0, 0, 2],
        [0, 6, 7, 3, 0, 1, 0, 0, 0],
        [0, 3, 0, 0, 0, 0, 2, 6, 0],
        [0, 0, 0, 0, 4, 6, 3, 0, 1],
        [0, 8, 0, 9, 5, 0, 0, 3, 6],
        [0, 5, 0, 0, 0, 4, 0, 0, 0],
        [0, 0, 2, 0, 7, 3, 5, 0, 0]]
    ],
            'hard': [
        [[0, 2, 0, 0, 0, 0, 1, 0, 3],
        [6, 3, 0, 0, 0, 0, 7, 0, 0],
        [7, 0, 0, 9, 0, 0, 0, 0, 6],
        [0, 0, 0, 0, 6, 0, 0, 0, 0],
        [0, 0, 0, 7, 0, 0, 9, 0, 0],
        [0, 9, 0, 0, 8, 0, 2, 0, 0],
        [0, 0, 9, 8, 5, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 0, 0, 1, 7],
        [0, 5, 1, 0, 0, 0, 3, 0, 9]]
    ]
        }
        self.current_puzzle_index = {'easy': 0, 'medium': 0, 'hard': 0}
        self.backtrack_count = 0  # Biến đếm số lần quay lui
        self.generate_puzzle('medium')  # Mặc định khởi tạo với mức medium

    def is_board_valid(self) -> bool:
        """Kiểm tra bảng Sudoku có hợp lệ không"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != 0:
                    num = self.board[i][j]
                    self.board[i][j] = 0
                    if not self.is_valid(i, j, num):
                        self.board[i][j] = num
                        return False
                    self.board[i][j] = num
        return True

    def solve_vanilla(self) -> bool:
        """Giải bằng backtracking thông thường"""
        empty = self.find_empty_vanilla()
        if not empty: 
            return True
        row, col = empty
        
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                if self.solve_vanilla(): 
                    return True
                self.board[row][col] = 0
        self.backtrack_count += 1  # Tăng khi không tìm thấy giá trị hợp lệ
        return False

    def solve_mrv(self) -> bool:
        """Giải bằng heuristic MRV"""
        self.empty_cells = []
        self.update_empty_cells()
        if not self.empty_cells: 
            return True
            
        _, row, col = heappop(self.empty_cells)
        valid_numbers = self.get_valid_numbers(row, col)
        for num in valid_numbers:
            self.board[row][col] = num
            if self.solve_mrv(): 
                return True
            self.board[row][col] = 0
        self.backtrack_count += 1  # Tăng khi không tìm thấy giá trị hợp lệ
        return False

    def find_empty_vanilla(self) -> Optional[Tuple[int, int]]:
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return (i, j)
        return None

    def update_empty_cells(self):
        """Cập nhật danh sách ô trống với số lượng giá trị hợp lệ"""
        self.empty_cells = []
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    num_options = len(self.get_valid_numbers(i, j))
                    heappush(self.empty_cells, (num_options, i, j))

    def get_valid_numbers(self, row: int, col: int) -> List[int]:
        used = set(self.board[row])
        used.update(self.board[i][col] for i in range(9))
        box_row, box_col = row//3*3, col//3*3
        used.update(self.board[i][j] for i in range(box_row, box_row+3) 
                      for j in range(box_col, box_col+3))
        return [num for num in range(1, 10) if num not in used]

    def is_valid(self, row: int, col: int, num: int) -> bool:
        if num in self.board[row]: 
            return False
        if any(self.board[i][col] == num for i in range(9)): 
            return False
        box_row, box_col = row//3*3, col//3*3
        for i in range(box_row, box_row+3):
            for j in range(box_col, box_col+3):
                if self.board[i][j] == num:
                    return False
        return True

    def generate_puzzle(self, difficulty: str, random_puzzle: bool = False) -> None:
        if not self.all_puzzles.get(difficulty):
            raise ValueError(f"Không có ma trận nào cho độ khó {difficulty}")
        
        self.board = deepcopy(self.all_puzzles[difficulty][0])  # Lấy đề bài đầu tiên
        self.initial_board = deepcopy(self.board)
        self.backtrack_count = 0
        
        if not self.is_board_valid():
            raise ValueError(f"Ma trận {difficulty} không hợp lệ!")

    # ================= PHẦN MEMORY ANALYSIS (CHỈ CHO TERMINAL) =================
    def measure_board_memory(self) -> dict:
        """Đo chính xác bộ nhớ sử dụng để lưu trữ bảng Sudoku"""
        # Tính toán theoretical memory
        board_size = 9 * 9 * sys.getsizeof(int())  # 9x9 integers
        empty_cells_estimated = len([1 for i in range(9) for j in range(9) if self.initial_board[i][j] == 0])
        
        # Đo practical memory
        gc.collect()
        tracemalloc.start()
        
        # Tạo multiple instances để đo chính xác
        boards = []
        for _ in range(5):  # Tạo 5 bản copy
            boards.append(deepcopy(self.initial_board))
        
        current, peak = tracemalloc.get_traced_memory()
        practical_memory = current // 5  # Chia trung bình
        
        tracemalloc.stop()
        del boards
        gc.collect()
        
        return {
            'theoretical_bytes': board_size,
            'practical_bytes': practical_memory,
            'empty_cells': empty_cells_estimated
        }

    def measure_search_memory(self, method: str) -> dict:
        """Đo bộ nhớ chi tiết trong quá trình tìm kiếm"""
        # Reset và chuẩn bị
        self.board = deepcopy(self.initial_board)
        self.backtrack_count = 0
        self.empty_cells = []
        
        # Force garbage collection
        for _ in range(3):
            gc.collect()
        
        # Bắt đầu đo memory
        tracemalloc.start()
        memory_snapshots = []
        
        # Đo memory trước khi search
        initial_memory = tracemalloc.get_traced_memory()[0]
        
        # Custom solve với memory tracking
        if method == 'mrv':
            solved = self._solve_mrv_with_memory_tracking(memory_snapshots)
        else:
            solved = self._solve_vanilla_with_memory_tracking(memory_snapshots)
        
        # Đo memory sau khi search
        final_current, peak_memory = tracemalloc.get_traced_memory()
        search_memory_used = final_current - initial_memory
        
        tracemalloc.stop()
        gc.collect()
        
        return {
            'method': method,
            'solved': solved,
            'search_memory_bytes': search_memory_used,
            'peak_memory_bytes': peak_memory,
            'memory_operations': len(memory_snapshots)
        }

    def _solve_vanilla_with_memory_tracking(self, memory_snapshots: list) -> bool:
        """Vanilla solve với memory tracking"""
        empty = self.find_empty_vanilla()
        if not empty:
            return True
            
        # Track memory tại mỗi recursive call
        current_memory = tracemalloc.get_traced_memory()[0]
        memory_snapshots.append(current_memory)
        
        row, col = empty
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                if self._solve_vanilla_with_memory_tracking(memory_snapshots):
                    return True
                self.board[row][col] = 0
        
        self.backtrack_count += 1
        return False

    def _solve_mrv_with_memory_tracking(self, memory_snapshots: list) -> bool:
        """MRV solve với memory tracking"""
        self.empty_cells = []
        self.update_empty_cells()
        
        # Track memory cho MRV operations
        current_memory = tracemalloc.get_traced_memory()[0]
        memory_snapshots.append(current_memory)
        
        if not self.empty_cells:
            return True
            
        _, row, col = heappop(self.empty_cells)
        valid_numbers = self.get_valid_numbers(row, col)
        
        for num in valid_numbers:
            self.board[row][col] = num
            if self._solve_mrv_with_memory_tracking(memory_snapshots):
                return True
            self.board[row][col] = 0
            
        self.backtrack_count += 1
        return False

    def memory_analysis_terminal(self, difficulty: str) -> dict:
        """Chuyên phân tích bộ nhớ cho terminal với thông tin chi tiết"""
        print(f"\n{'='*60}")
        print(f"COMPREHENSIVE MEMORY ANALYSIS FOR {difficulty.upper()}")
        print(f"{'='*60}")
        
        self.generate_puzzle(difficulty)
        
        # 1. Board Memory Analysis
        print(f"📋 BOARD STORAGE ANALYSIS:")
        board_mem_info = self.measure_board_memory()
        print(f"   • Theoretical Memory: {board_mem_info['theoretical_bytes']:,} bytes ({board_mem_info['theoretical_bytes']/1024:.2f} KB)")
        print(f"   • Practical Memory: {board_mem_info['practical_bytes']:,} bytes ({board_mem_info['practical_bytes']/1024:.2f} KB)")
        print(f"   • Empty Cells: {board_mem_info['empty_cells']} cells")
        
        # 2. Search Memory Analysis
        print(f"\n🔍 SEARCH MEMORY ANALYSIS:")
        print("   Measuring Vanilla Backtracking...")
        vanilla_result = self.measure_search_memory('vanilla')
        
        print("   Measuring MRV Heuristic...")
        mrv_result = self.measure_search_memory('mrv')
        
        if not vanilla_result['solved'] or not mrv_result['solved']:
            print("❌ Không thể giải được puzzle!")
            return {}
        
        # 3. Detailed Comparison (đã loại bỏ Max Operation)
        search_ratio = vanilla_result['search_memory_bytes'] / max(mrv_result['search_memory_bytes'], 1)
        peak_ratio = vanilla_result['peak_memory_bytes'] / max(mrv_result['peak_memory_bytes'], 1)
        
        print(f"\n💾 DETAILED MEMORY COMPARISON:")
        print(f"┌─────────────────────┬─────────────────┬─────────────────┬─────────────────┐")
        print(f"│ Algorithm           │ Search Memory   │ Peak Memory     │ Memory Ops      │")
        print(f"├─────────────────────┼─────────────────┼─────────────────┼─────────────────┤")
        print(f"│ Vanilla Backtrack   │ {vanilla_result['search_memory_bytes']:>8,} bytes │ {vanilla_result['peak_memory_bytes']:>8,} bytes │ {vanilla_result['memory_operations']:>8,} ops   │")
        print(f"│ MRV Heuristic       │ {mrv_result['search_memory_bytes']:>8,} bytes │ {mrv_result['peak_memory_bytes']:>8,} bytes │ {mrv_result['memory_operations']:>8,} ops   │")
        print(f"└─────────────────────┴─────────────────┴─────────────────┴─────────────────┘")
        
        print(f"\n🚀 MEMORY EFFICIENCY ANALYSIS:")
        print(f"   📊 Search Memory: MRV uses {search_ratio:.2f}x {'less' if search_ratio > 1 else 'more'} memory than Vanilla")
        print(f"   📈 Peak Memory: MRV uses {peak_ratio:.2f}x {'less' if peak_ratio > 1 else 'more'} peak memory")
        print(f"   🔄 Memory Operations: Vanilla({vanilla_result['memory_operations']:,}) vs MRV({mrv_result['memory_operations']:,})")
        
        # 4. Memory per Operation Analysis
        vanilla_mem_per_op = vanilla_result['search_memory_bytes'] / max(vanilla_result['memory_operations'], 1)
        mrv_mem_per_op = mrv_result['search_memory_bytes'] / max(mrv_result['memory_operations'], 1)
        
        print(f"\n📐 MEMORY EFFICIENCY PER OPERATION:")
        print(f"   • Vanilla: {vanilla_mem_per_op:.2f} bytes/operation")
        print(f"   • MRV: {mrv_mem_per_op:.2f} bytes/operation")
        print(f"   • Efficiency Ratio: {vanilla_mem_per_op/max(mrv_mem_per_op, 0.01):.2f}x")
        
        return {
            'difficulty': difficulty,
            'board_memory': board_mem_info,
            'vanilla_search': vanilla_result,
            'mrv_search': mrv_result,
            'memory_efficiency_ratio': search_ratio,
            'peak_memory_ratio': peak_ratio
        }

    # ================= PHẦN BENCHMARK (CHO GUI) =================
    def benchmark(self, method: str) -> dict:
        """Benchmark đơn giản cho GUI - chỉ đo thời gian và backtrack"""
        self.board = deepcopy(self.initial_board)
        self.backtrack_count = 0
        self.empty_cells = []

        start_time = time.perf_counter()
        if method == 'mrv':
            solved = self.solve_mrv()
        else:
            solved = self.solve_vanilla()
        elapsed = time.perf_counter() - start_time

        return {
            'time': elapsed,
            'solved': solved,
            'backtracks': self.backtrack_count
        }

    def is_solved(self) -> bool:
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0 or not self.is_valid(i, j, self.board[i][j]):
                    return False
        return True

# ================= PHẦN GIAO DIỆN =================
class SudokuApp:
    def __init__(self, root):
        self.solver = SudokuSolver()
        self.root = root
        self.root.title("Sudoku Solver - Đề tài AI")

        sudoku_frame = tk.Frame(root, bd=1, relief='solid', bg='black')
        sudoku_frame.grid(row=0, column=0, padx=20, pady=20)
        
        self.block_frames = [[None for _ in range(3)] for _ in range(3)]
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        
        for block_row in range(3):
            for block_col in range(3):
                block_frame = tk.Frame(sudoku_frame, bd=1, relief='solid', bg='#999999')
                block_frame.grid(row=block_row, column=block_col, padx=1, pady=1)
                self.block_frames[block_row][block_col] = block_frame
                
                for i in range(3):
                    for j in range(3):
                        row = block_row * 3 + i
                        col = block_col * 3 + j
                        cell = tk.Entry(
                            block_frame, width=4, font=('Arial', 15), justify='center',
                            relief='flat', bd=0, bg='#f0f0f0' if (block_row + block_col) % 2 == 0 else '#ffffff'
                        )
                        cell.grid(row=i, column=j, padx=1, pady=1)
                        self.cells[row][col] = cell

        control_frame = tk.Frame(root)
        control_frame.grid(row=10, column=0, columnspan=9, pady=10)
        
        self.difficulty = tk.StringVar(value='medium')
        difficulty_frame = tk.Frame(root)
        difficulty_frame.grid(row=9, column=0, columnspan=9, pady=5)
        tk.Label(difficulty_frame, text="Độ khó:").pack(side=tk.LEFT)
        difficulties = [('Dễ', 'easy'), ('Trung Bình', 'medium'), ('Khó', 'hard')]
        for text, mode in difficulties:
            tk.Radiobutton(difficulty_frame, text=text, variable=self.difficulty, 
                           value=mode).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Giải (Backtracking)", command=lambda: self.solve('vanilla')).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Giải (MRV)", command=lambda: self.solve('mrv')).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Tạo mới", command=self.new_puzzle).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="So sánh hiệu năng", command=self.run_benchmark).pack(side=tk.LEFT, padx=5)
        
        self.stats_label = tk.Label(root, text="", font=('Arial', 10))
        self.stats_label.grid(row=11, column=0, columnspan=9)

    def solve(self, method='mrv'):
        try:
            for i in range(9):
                for j in range(9):
                    val = self.cells[i][j].get()
                    self.solver.board[i][j] = int(val) if val else 0

            if not self.solver.is_board_valid():
                messagebox.showerror("Lỗi", "Bảng Sudoku không hợp lệ!")
                return

            self.solver.backtrack_count = 0
            start_time = time.perf_counter()
            timeout = 10
            if method == 'mrv':
                solved = self.solver.solve_mrv()
            else:
                solved = self.solver.solve_vanilla()
            elapsed = time.perf_counter() - start_time

            if elapsed > timeout:
                messagebox.showwarning("Cảnh báo", f"Phương pháp {method.upper()} mất quá nhiều thời gian!")
                return

            if solved:
                self.update_board()
                self.stats_label.config(
                    text=f"{method.upper()}: Giải xong trong {elapsed:.4f}s ({self.solver.backtrack_count} backtracks)", 
                    fg='green'
                )
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy lời giải!")
        except ValueError:
            messagebox.showerror("Lỗi", "Chỉ nhập số từ 1-9 hoặc để trống")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    def new_puzzle(self):
        try:
            difficulty = self.difficulty.get()
            self.solver.generate_puzzle(difficulty)
            self.update_board()
            self.stats_label.config(text=f"Đã tạo đề bài mức {difficulty.upper()}", fg='blue')
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def update_board(self):
        for i in range(9):
            for j in range(9):
                self.cells[i][j].delete(0, tk.END)
                if self.solver.board[i][j] != 0:
                    self.cells[i][j].insert(0, str(self.solver.board[i][j]))

    def run_benchmark(self):
        """Chỉ đo thời gian và backtrack - không đo memory"""
        progress = tk.Toplevel(self.root)
        progress.title("Đang chạy Benchmark...")
        tk.Label(progress, text="Đang so sánh hiệu năng, vui lòng chờ...").pack(pady=10)
        progress_bar = ttk.Progressbar(progress, length=300, mode='indeterminate')
        progress_bar.pack(pady=10)
        progress_bar.start()

        def run_benchmark():
            results = []
            for diff in ['easy', 'medium', 'hard']:
                try:
                    self.solver.generate_puzzle(diff)
                    
                    vanilla = self.solver.benchmark('vanilla')
                    self.solver.board = deepcopy(self.solver.initial_board)
                    mrv = self.solver.benchmark('mrv')
                    
                    if not vanilla['solved'] or not mrv['solved']:
                        results.append(f"{diff.upper()}: Không giải được!")
                        continue
                        
                    results.append(
                        f"{diff.upper()}\n"
                        f"- Backtracking: {vanilla['time']:.4f}s ({vanilla['backtracks']} backtracks)\n"
                        f"- MRV: {mrv['time']:.4f}s ({mrv['backtracks']} backtracks)\n"
                        f"→ MRV nhanh hơn {vanilla['time']/max(mrv['time'], 0.0001):.1f}x"
                    )
                    
                except Exception as e:
                    results.append(f"{diff.upper()}: Lỗi - {str(e)}")
                    
            progress.destroy()
            messagebox.showinfo("Kết quả Benchmark", "\n".join(results))

        progress.after(100, run_benchmark)
        progress.wait_window()

    @staticmethod
    def run_memory_analysis_terminal(difficulty: str):
        """Chạy phân tích bộ nhớ qua terminal"""
        if difficulty not in ['easy', 'medium', 'hard']:
            print("Độ khó phải là: easy, medium, hoặc hard")
            return
            
        solver = SudokuSolver()
        solver.memory_analysis_terminal(difficulty)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sudoku Solver - Memory Analysis")
    parser.add_argument('--memory', type=str, help='Phân tích bộ nhớ cho độ khó: easy, medium, hoặc hard')

    args = parser.parse_args()

    if args.memory:
        # Chạy memory analysis qua terminal
        SudokuApp.run_memory_analysis_terminal(args.memory.lower())
    else:
        # Chạy GUI
        root = tk.Tk()
        app = SudokuApp(root)
        root.mainloop()