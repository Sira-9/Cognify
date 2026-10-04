"""
Curated Seed Data for AdaptiveLearn AI.
Provides rich, production-grade learning content for Computer Science topics:
- Operating Systems (Virtual Memory & Paging)
- Data Structures (Binary Trees & BSTs)
- Computer Architecture (Instruction Pipelining)
- C++ (Exception Handling & RAII)
- C Programming (Pointers & Memory Allocation)
"""

DEMO_TOPICS = [
    {
        "subject": "Operating Systems",
        "topic_name": "Virtual Memory & Paging",
        "description": "How modern operating systems isolate process memory, translate virtual addresses to physical RAM, and manage page faults.",
        "difficulty_level": "intermediate",
        "concepts": [
            {
                "id": "os_vm_1",
                "title": "Virtual Memory & Address Translation",
                "difficulty_level": "basic",
                "simple_explanation": "Virtual memory gives each program the illusion that it has a large, contiguous block of RAM all to itself. In reality, the OS breaks memory into fixed-size chunks called 'pages' and maps them to physical frames in actual RAM.",
                "important_points": [
                    "Virtual Address is divided into a Page Number (VPN) and an Offset.",
                    "Physical Address is divided into a Frame Number (PFN) and an Offset.",
                    "The Offset is identical in both addresses because page size equals frame size.",
                    "Translation is performed automatically by hardware (the MMU: Memory Management Unit)."
                ],
                "visual_representation": """
+----------------------- Virtual Address -----------------------+
|   Virtual Page Number (VPN)   |       Page Offset (D)        |
+-------------------------------+------------------------------+
                |                                      |
                v [MMU Page Table Lookup]              |
+-------------------------------- Physical Address ------------+
|   Physical Frame Number (PFN) |       Page Offset (D)        |
+-------------------------------+------------------------------+
""",
                "real_world_analogy": "Imagine a university course code (like 'CS-101') vs the actual lecture hall room number ('Hall 3B'). Students refer to 'CS-101' regardless of which physical hall it gets scheduled in each semester.",
                "concrete_example": "If page size is 4 KB (2^12 bytes), the lower 12 bits of any address are the Offset. If Virtual Address is 0x1234, Offset is 0x234 and VPN is 0x1. The MMU looks up VPN 0x1 in the Page Table to find the physical frame.",
                "key_takeaway": "Virtual addresses isolate programs and decouple program memory layouts from physical RAM placement via the MMU.",
                "misconceptions": [
                    "Myth: Virtual memory is just the swap file on your hard drive. (Truth: Virtual memory is the entire abstraction of isolated address spaces; swapping is merely the overflow mechanism)."
                ],
                "questions": [
                    {
                        "id": "q_vm_1",
                        "difficulty": "Easy",
                        "question": "In a paged virtual memory system with 4 KB pages, what part of the virtual address remains unchanged during address translation?",
                        "options": [
                            "The Page Number (VPN)",
                            "The Page Offset",
                            "The Frame Number (PFN)",
                            "The Segment Selector"
                        ],
                        "correct_index": 1,
                        "explanation": "Because page size equals physical frame size (4 KB), the offset within the page is identical in both virtual and physical addresses.",
                        "hint_tier_1": "Think about where inside the page an individual byte is located.",
                        "hint_tier_2": "The translation replaces the page identifier with a physical frame identifier, but distance within the frame stays constant.",
                        "hint_tier_3": "Formula: Physical Address = (Frame Number * Page Size) + Offset. The Offset never changes.",
                        "worked_example": "Let VA = 0x2048 with 4096-byte pages. Offset is 0x048. If VPN 2 maps to Frame 7, Physical Address is Frame 7 base + 0x048. Offset is conserved."
                    },
                    {
                        "id": "q_vm_2",
                        "difficulty": "Medium",
                        "question": "If a system has a 32-bit virtual address space and uses 4 KB (2^12 bytes) pages, how many virtual pages can exist in a single process address space?",
                        "options": [
                            "1,048,576 (2^20) pages",
                            "4,096 (2^12) pages",
                            "65,536 (2^16) pages",
                            "16,777,216 (2^24) pages"
                        ],
                        "correct_index": 0,
                        "explanation": "32 bits total minus 12 bits for the offset leaves 20 bits for the Virtual Page Number (VPN). 2^20 = 1,048,576 pages.",
                        "hint_tier_1": "Subtract the offset bits from the total virtual address bits.",
                        "hint_tier_2": "32 total bits - 12 offset bits = bits for Page Number.",
                        "hint_tier_3": "2^(32 - 12) = 2^20 = 1,048,576.",
                        "worked_example": "A 32-bit address can address 4 GB. 4 GB / 4 KB = (2^32) / (2^12) = 2^20 = 1,048,576 pages."
                    },
                    {
                        "id": "q_vm_3",
                        "difficulty": "Hard",
                        "question": "What primary security and stability benefit does each process having its own private page table provide?",
                        "options": [
                            "It speeds up CPU clock cycles during arithmetic calculations",
                            "It completely eliminates the need for physical RAM",
                            "It prevents processes from reading or corrupting each other's memory",
                            "It compresses disk files automatically during program execution"
                        ],
                        "correct_index": 2,
                        "explanation": "Because page tables map each process's virtual pages only to authorized physical frames, a process cannot access another process's memory without explicit shared memory setup.",
                        "hint_tier_1": "Focus on isolation between different applications running at the same time.",
                        "hint_tier_2": "Can process A write into process B's variables if process A's page table doesn't map to process B's frames?",
                        "hint_tier_3": "Isolation ensures memory protection: illegal memory references trigger segmentation faults.",
                        "worked_example": "Process 1 access to VA 0x1000 maps to Frame 12. Process 2 access to VA 0x1000 maps to Frame 45. They are completely separated."
                    }
                ]
            },
            {
                "id": "os_vm_2",
                "title": "Page Tables & Multi-Level Paging",
                "difficulty_level": "intermediate",
                "simple_explanation": "A Page Table is an in-memory data structure that records the mapping from Virtual Page Numbers to Physical Frame Numbers. Because a flat page table would be too large, systems use Multi-Level Page Tables to allocate table structures only for memory regions that are actually in use.",
                "important_points": [
                    "A flat page table for a 32-bit system with 4-byte entries takes 4 MB per process.",
                    "Multi-level paging uses a hierarchy (e.g. Page Directory -> Page Table -> Frame).",
                    "Invalid address regions don't need second-level page tables, saving huge amounts of RAM.",
                    "Trade-off: Address translation requires multiple memory accesses if not cached."
                ],
                "visual_representation": """
CR3 Register (Points to Page Directory)
       |
       v
+--------------+        +--------------+
| Page Directory| -----> |  Page Table  | -----> Physical Frame in RAM
+--------------+        +--------------+
| Entry 0 (Dir) |        | PTE 0 (PFN)  |
| Entry 1 (Dir) |        | PTE 1 (PFN)  |
+--------------+        +--------------+
""",
                "real_world_analogy": "Think of a phone book or an encyclopedia index. Instead of listing every person on earth in one massive index, you have a country index, then a city index, then local listings.",
                "concrete_example": "In x86 32-bit two-level paging: 10 bits for Directory Index, 10 bits for Page Table Index, 12 bits for Offset (10 + 10 + 12 = 32 bits). If a process only uses 8 MB of memory, only 2 second-level tables are allocated instead of 1024!",
                "key_takeaway": "Multi-level page tables dramatically reduce memory overhead by allocating page tables on demand for sparsely populated address spaces.",
                "misconceptions": [
                    "Myth: Multi-level page tables speed up address translation. (Truth: They actually slow it down because of extra memory lookups, which is why hardware TLBs are necessary)."
                ],
                "questions": [
                    {
                        "id": "q_pt_1",
                        "difficulty": "Easy",
                        "question": "What is the primary motivation for using a multi-level page table instead of a single flat page table?",
                        "options": [
                            "To decrease memory consumption for sparse address spaces",
                            "To make memory translations faster without hardware support",
                            "To increase the size of physical hard drives",
                            "To avoid using virtual addresses completely"
                        ],
                        "correct_index": 0,
                        "explanation": "Most programs use only a fraction of their virtual address space. Multi-level tables only allocate page tables for address ranges currently in use.",
                        "hint_tier_1": "Consider how much empty or unused space exists in a 64-bit or 32-bit program.",
                        "hint_tier_2": "A flat table must store entries for unused virtual space. Multi-level tables prune unused branches.",
                        "hint_tier_3": "Saving RAM space is the main reason; hierarchical structures omit empty sub-tables.",
                        "worked_example": "In a 32-bit process using 4 MB out of 4 GB, flat table requires 4 MB overhead. Two-level table requires 4 KB directory + 4 KB table = 8 KB overhead!"
                    },
                    {
                        "id": "q_pt_2",
                        "difficulty": "Medium",
                        "question": "In a 2-level paging scheme, how many memory accesses are required to read a single data word from RAM on a cold lookup (without cache/TLB)?",
                        "options": [
                            "1 access",
                            "2 accesses",
                            "3 accesses",
                            "4 accesses"
                        ],
                        "correct_index": 2,
                        "explanation": "1st access: read Page Directory Entry. 2nd access: read Page Table Entry. 3rd access: read the actual target data from physical RAM.",
                        "hint_tier_1": "Trace each step from directory to table to final memory location.",
                        "hint_tier_2": "Access 1 = Directory. Access 2 = Table. What about the actual data?",
                        "hint_tier_3": "Total = N levels + 1 data fetch = 2 + 1 = 3.",
                        "worked_example": "Lookup Directory in RAM (1) -> Lookup Page Table in RAM (2) -> Fetch data word at Physical Address (3)."
                    }
                ]
            },
            {
                "id": "os_vm_3",
                "title": "Translation Lookaside Buffer (TLB)",
                "difficulty_level": "intermediate",
                "simple_explanation": "The Translation Lookaside Buffer (TLB) is an ultra-fast hardware cache located right on the CPU chip. It stores recent Virtual-to-Physical page translations so the CPU doesn't have to navigate multi-level page tables in slow RAM on every single instruction.",
                "important_points": [
                    "TLB hit rate in modern workloads is typically 98-99%.",
                    "A TLB hit takes ~1 clock cycle; a TLB miss takes 10-100+ cycles (page table walk).",
                    "When context switching between processes, the TLB must be flushed or use Address Space Identifiers (ASID).",
                    "Effective Memory Access Time (EMAT) depends heavily on TLB hit ratio."
                ],
                "visual_representation": """
Virtual Address
      |
      +---> [ Check TLB Cache ] ---- HIT ----> Fast Physical Address (<1ns)
                   |
                  MISS
                   v
          [ Memory Page Walk ] --------------> Read from RAM (50ns) + Refill TLB
""",
                "real_world_analogy": "Your browser's address bar autocomplete. Instead of typing the full 40-character URL or searching DNS every time, the top 5 sites you visited this morning load instantly from local memory.",
                "concrete_example": "If TLB hit time is 1ns, memory access is 50ns, and hit rate is 98%: Effective Access Time = 0.98 * (1 + 50) + 0.02 * (1 + 50 + 50) = 49.98 + 2.02 = 52ns, compared to 100ns without TLB!",
                "key_takeaway": "Without the TLB, paged virtual memory would cut CPU performance in half due to repeated page table lookups.",
                "misconceptions": [
                    "Myth: The TLB caches program data and code. (Truth: The TLB strictly caches address translations: VPN -> PFN mappings)."
                ],
                "questions": [
                    {
                        "id": "q_tlb_1",
                        "difficulty": "Easy",
                        "question": "What exactly does a Translation Lookaside Buffer (TLB) cache?",
                        "options": [
                            "User files and disk sectors",
                            "Recent Virtual Page to Physical Frame address translations",
                            "Entire programs compiled into machine code",
                            "Network packets waiting to be sent"
                        ],
                        "correct_index": 1,
                        "explanation": "The TLB is a dedicated MMU cache storing mappings from Virtual Page Numbers (VPN) to Physical Frame Numbers (PFN).",
                        "hint_tier_1": "Think about what translation means in virtual memory.",
                        "hint_tier_2": "It stores VPN -> PFN mappings to avoid memory walks.",
                        "hint_tier_3": "It is an address translation cache, not a data cache.",
                        "worked_example": "Input VPN -> TLB returns PFN in 1 cycle."
                    },
                    {
                        "id": "q_tlb_2",
                        "difficulty": "Medium",
                        "question": "If TLB search takes 2ns, physical memory access takes 80ns, and the TLB hit ratio is 95%, what is the Effective Memory Access Time (EMAT) for a single-level page table?",
                        "options": [
                            "86ns",
                            "42ns",
                            "164ns",
                            "120ns"
                        ],
                        "correct_index": 0,
                        "explanation": "Hit time = 2ns (TLB) + 80ns (Data) = 82ns. Miss time = 2ns (TLB) + 80ns (Page Table) + 80ns (Data) = 162ns. EMAT = 0.95 * 82 + 0.05 * 162 = 77.9 + 8.1 = 86ns.",
                        "hint_tier_1": "Calculate the time for a hit (TLB + 1 RAM access) and a miss (TLB + 2 RAM accesses).",
                        "hint_tier_2": "Hit: 82ns. Miss: 162ns. Weight them by 0.95 and 0.05.",
                        "hint_tier_3": "EMAT = 0.95*(82) + 0.05*(162) = 77.9 + 8.1 = 86ns.",
                        "worked_example": "Weighted average: 0.95 * 82ns + 0.05 * 162ns = 86ns."
                    }
                ]
            },
            {
                "id": "os_vm_4",
                "title": "Page Fault Handling & Replacement Algorithms",
                "difficulty_level": "advanced",
                "simple_explanation": "A Page Fault occurs when a program accesses a valid virtual page that is currently not loaded in physical RAM (its 'present bit' is 0). The CPU generates a hardware trap to the OS kernel, which fetches the page from disk/swap into an available frame, updates the page table, and resumes execution.",
                "important_points": [
                    "Page fault is an exception, NOT a program crash (unlike segmentation fault).",
                    "If RAM is full, the OS must choose a 'victim' page to evict using replacement algorithms.",
                    "LRU (Least Recently Used) evicts the page that hasn't been accessed for the longest time.",
                    "FIFO (First-In, First-Out) can suffer from Belady's Anomaly (more frames -> more page faults!).",
                    "Thrashing occurs when the system spends more time swapping pages than executing instructions."
                ],
                "visual_representation": """
Process Accesses Memory
           |
         [ MMU ] ---> Valid Bit = 0? (Page Fault Trap!)
           |
           v
  +------------------ OS Kernel Handler ------------------+
  | 1. Find free frame (or evict victim via LRU/Clock)    |
  | 2. Read missing page from Disk/SSD into RAM           |
  | 3. Set Present Bit = 1, update PFN in Page Table      |
  | 4. Restart the faulting instruction seamlessly        |
  +-------------------------------------------------------+
""",
                "real_world_analogy": "A chef's prep counter. If the recipe calls for saffron that isn't on the counter, the chef pauses, walks to the pantry to grab it, sets it on the counter (maybe returning an unused spice back to the shelf), and continues cooking.",
                "concrete_example": "With 3 frames and page reference sequence: 1, 2, 3, 4, 1, 2. When page 4 arrives, under LRU, page 1 is evicted (least recently used). Under FIFO, page 1 is evicted because it arrived first.",
                "key_takeaway": "Page fault handling transparently bridges fast RAM and secondary storage, but excessive faults cause thrashing.",
                "misconceptions": [
                    "Myth: Every page fault means the computer crashed or ran out of memory. (Truth: Page faults are the standard lazy-loading mechanism used by OS kernels for normal execution)."
                ],
                "questions": [
                    {
                        "id": "q_pf_1",
                        "difficulty": "Easy",
                        "question": "What is a 'Page Fault' in an operating system?",
                        "options": [
                            "A permanent physical hardware failure in RAM chips",
                            "An interrupt triggered when a requested virtual page is not currently in physical RAM",
                            "A syntax error in the source code of an application",
                            "An error caused by a computer virus"
                        ],
                        "correct_index": 1,
                        "explanation": "A page fault is an architecture trap notifying the OS that the requested page's Present Bit is 0, so it must be brought in from secondary storage.",
                        "hint_tier_1": "Is it a crash or an expected operating system event?",
                        "hint_tier_2": "The page is valid, but simply resides on disk rather than RAM.",
                        "hint_tier_3": "Present bit = 0 generates a page fault trap so the kernel can load it.",
                        "worked_example": "Program accesses page X -> MMU sees valid=0 -> page fault trap -> kernel loads page X from disk."
                    },
                    {
                        "id": "q_pf_2",
                        "difficulty": "Medium",
                        "question": "Which page replacement phenomenon demonstrates that increasing the number of physical page frames can paradoxically increase the number of page faults under FIFO?",
                        "options": [
                            "Amdahl's Law",
                            "Moore's Law",
                            "Belady's Anomaly",
                            "Dijkstra's Starvation"
                        ],
                        "correct_index": 2,
                        "explanation": "Belady's Anomaly is the counter-intuitive phenomenon where allocating more page frames leads to more page faults under certain FIFO reference strings.",
                        "hint_tier_1": "Named after a famous computer scientist studying FIFO page replacement.",
                        "hint_tier_2": "It starts with the letter 'B'.",
                        "hint_tier_3": "László Bélády discovered this in 1969.",
                        "worked_example": "Reference string 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5 yields 9 faults with 3 frames, but 10 faults with 4 frames under FIFO!"
                    },
                    {
                        "id": "q_pf_3",
                        "difficulty": "Hard",
                        "question": "What is 'thrashing' in an operating system, and how is it caused?",
                        "options": [
                            "CPU overheating due to high clock multiplier frequencies",
                            "The system spending the vast majority of its time swapping pages in/out rather than doing useful computation",
                            "Data corruption caused by writing to disk sectors too rapidly",
                            "A denial of service attack flooding network interfaces"
                        ],
                        "correct_index": 1,
                        "explanation": "Thrashing occurs when the sum of working sets across all active processes exceeds physical RAM capacity, causing continuous page faults and near-zero CPU progress.",
                        "hint_tier_1": "Think about what happens when active processes need more RAM than is physically installed.",
                        "hint_tier_2": "Every page access causes a page fault, keeping the disk active 100% of the time while CPU waits.",
                        "hint_tier_3": "Working set > Physical RAM => perpetual swapping = thrashing.",
                        "worked_example": "Active processes require 12 GB working set, but computer has 8 GB RAM. The OS continuously evicts and reloads pages every millisecond."
                    }
                ]
            }
        ]
    },
    {
        "subject": "Computer Science",
        "topic_name": "Data Structures - Trees & Binary Search Trees",
        "description": "Master hierarchical tree structures, binary search tree invariants, traversal strategies, and self-balancing concepts.",
        "difficulty_level": "intermediate",
        "concepts": [
            {
                "id": "ds_tree_1",
                "title": "Tree Fundamentals & Terminology",
                "difficulty_level": "basic",
                "simple_explanation": "A Tree is a non-linear hierarchical data structure consisting of nodes connected by edges. It begins at a single top node called the 'Root' and has no cycles. Every node (except the root) has exactly one parent.",
                "important_points": [
                    "Root: Topmost node without any parent.",
                    "Leaf: Node with 0 children.",
                    "Height: Length of longest path from node to a leaf.",
                    "Depth: Length of path from root to that node.",
                    "A tree with N nodes always has exactly N - 1 edges."
                ],
                "visual_representation": """
        [ A ]  <-- Root (Depth 0, Height 2)
       /     \\
    [ B ]   [ C ]
    /   \\       \\
  [ D ] [ E ]   [ F ]  <-- Leaves (Height 0)
""",
                "real_world_analogy": "A corporate organizational chart (CEO at root, VPs as children, managers, and individual contributors as leaf nodes) or a file system directory structure.",
                "concrete_example": "A directory '/home/user/documents': '/' is the root, 'home' is a child of root, 'user' is a child of 'home', and 'documents' is a leaf folder.",
                "key_takeaway": "Trees represent hierarchical relationships efficiently with N-1 edges and zero cycles.",
                "misconceptions": [
                    "Myth: A tree can have circular links between nodes. (Truth: If it has cycles, it is a graph, not a tree)."
                ],
                "questions": [
                    {
                        "id": "q_tr_1",
                        "difficulty": "Easy",
                        "question": "How many edges does an undirected tree with 15 nodes contain?",
                        "options": [
                            "15 edges",
                            "14 edges",
                            "16 edges",
                            "30 edges"
                        ],
                        "correct_index": 1,
                        "explanation": "Any tree with N nodes has exactly N - 1 edges because every node except the root has exactly one incoming edge.",
                        "hint_tier_1": "Recall the fundamental property relating nodes and edges in any valid tree.",
                        "hint_tier_2": "Every node except the root connects to its parent via 1 edge.",
                        "hint_tier_3": "Formula: Edges = Nodes - 1 = 15 - 1 = 14.",
                        "worked_example": "For 3 nodes: A-B-C requires 2 edges. For N nodes: N - 1 edges."
                    },
                    {
                        "id": "q_tr_2",
                        "difficulty": "Medium",
                        "question": "What is the maximum number of nodes in a binary tree of height H (where a single root node has height 0)?",
                        "options": [
                            "2^H",
                            "2^(H + 1) - 1",
                            "2^H - 1",
                            "H^2 + 1"
                        ],
                        "correct_index": 1,
                        "explanation": "At depth 0: 1 node (2^0). At depth 1: 2 nodes (2^1)... Sum = 2^0 + 2^1 + ... + 2^H = 2^(H+1) - 1.",
                        "hint_tier_1": "Test with height 0 (single node) and height 1 (root + 2 children = 3 nodes).",
                        "hint_tier_2": "For H=0: 2^(0+1)-1 = 1 node. For H=1: 2^(1+1)-1 = 3 nodes.",
                        "hint_tier_3": "Sum of powers of 2 from 0 to H is 2^(H+1) - 1.",
                        "worked_example": "H=2: Depth 0 (1) + Depth 1 (2) + Depth 2 (4) = 7 nodes = 2^3 - 1."
                    }
                ]
            },
            {
                "id": "ds_tree_2",
                "title": "Binary Search Trees (BST) & Search Invariants",
                "difficulty_level": "intermediate",
                "simple_explanation": "A Binary Search Tree (BST) is a binary tree where every node obeys the BST Invariant: all values in the Left subtree are strictly smaller than the node, and all values in the Right subtree are strictly greater than the node.",
                "important_points": [
                    "BST Invariant must hold for ALL descendants, not just immediate children.",
                    "Search, Insert, and Delete average time complexity is O(log N).",
                    "Worst-case time complexity is O(N) when inserted in sorted order (skewed tree / degenerate linked list).",
                    "An In-Order traversal of a BST always visits nodes in ascending sorted order."
                ],
                "visual_representation": """
        [ 50 ]
       /      \\
    [ 30 ]    [ 70 ]
    /    \\    /    \\
  [ 20 ] [40][ 60 ][ 80 ]
All left < 50 < All right
""",
                "real_world_analogy": "Playing the 'higher or lower' number guessing game between 1 and 100. Guess 50: if told 'lower', you eliminate 51-100 and search only 1-49.",
                "concrete_example": "Searching for 40 in the visual tree above: 40 < 50 (go left to 30) -> 40 > 30 (go right to 40) -> Found! Total comparisons: 2.",
                "key_takeaway": "The BST invariant halves the remaining search space at each balanced step, delivering O(log N) search operations.",
                "misconceptions": [
                    "Myth: If node->left < node and node->right > node, it's automatically a valid BST. (Truth: The condition must hold for EVERY node in the subtrees; e.g. root 50, left child 30, right child of 30 cannot be 60!)."
                ],
                "questions": [
                    {
                        "id": "q_bst_1",
                        "difficulty": "Easy",
                        "question": "Which tree traversal order on a valid Binary Search Tree outputs values in strictly ascending sorted order?",
                        "options": [
                            "Pre-order (Root, Left, Right)",
                            "Post-order (Left, Right, Root)",
                            "In-order (Left, Root, Right)",
                            "Level-order (Breadth-First)"
                        ],
                        "correct_index": 2,
                        "explanation": "In-order traversal visits the Left subtree (all smaller elements), then the Root, then the Right subtree (all larger elements), yielding sorted order.",
                        "hint_tier_1": "Think about where the root should be visited relative to its smaller left and larger right children.",
                        "hint_tier_2": "Smallest elements are on the left; largest are on the right.",
                        "hint_tier_3": "Left -> Root -> Right is the In-Order traversal.",
                        "worked_example": "Tree with Root 5, Left 3, Right 8. In-order visits 3, then 5, then 8. Perfectly sorted!"
                    },
                    {
                        "id": "q_bst_2",
                        "difficulty": "Medium",
                        "question": "If elements [10, 20, 30, 40, 50] are inserted sequentially into an initially empty standard BST without balancing, what is the search time complexity?",
                        "options": [
                            "O(1)",
                            "O(log N)",
                            "O(N)",
                            "O(N log N)"
                        ],
                        "correct_index": 2,
                        "explanation": "Sequential sorted insertion creates a degenerate skewed tree resembling a linked list where every node is a right child, degrading search to O(N).",
                        "hint_tier_1": "Draw the tree structure created by inserting 10, then 20, then 30...",
                        "hint_tier_2": "Each new element is greater than all previous elements, so it always goes to the right.",
                        "hint_tier_3": "The tree degrades into a straight line (linked list) of height N.",
                        "worked_example": "10 -> right 20 -> right 30 -> right 40 -> right 50. Searching for 50 requires visiting all 5 nodes: O(N)."
                    }
                ]
            },
            {
                "id": "ds_tree_3",
                "title": "Balanced Trees & AVL Rotations",
                "difficulty_level": "advanced",
                "simple_explanation": "Self-balancing binary search trees (like AVL trees) automatically maintain an O(log N) height by performing tree rotations whenever an insertion or deletion causes the Balance Factor (Height of Left - Height of Right) to exceed {-1, 0, +1}.",
                "important_points": [
                    "Balance Factor = Height(Left Subtree) - Height(Right Subtree).",
                    "An AVL node is balanced if Balance Factor is -1, 0, or +1.",
                    "Four rotation types: Single Left (LL), Single Right (RR), Left-Right (LR), and Right-Left (RL).",
                    "Rotations take O(1) time and preserve the BST invariant perfectly."
                ],
                "visual_representation": """
Right Rotation (LL Case):
      [ 30 ]                    [ 20 ]
     /                         /      \\
   [ 20 ]       ===>         [ 10 ]   [ 30 ]
   /
 [ 10 ]
""",
                "real_world_analogy": "A physical balance scale. If the left side becomes two weights heavier than the right, you pivot the fulcrum or redistribute one weight to keep the scale level.",
                "concrete_example": "Inserting 30, 20, 10 into an empty AVL tree creates an imbalance at node 30 (Balance Factor = +2). A single Right Rotation pivots node 20 to the top, making 10 its left child and 30 its right child. Height drops from 3 to 2!",
                "key_takeaway": "AVL trees guarantee worst-case O(log N) operations by strictly enforcing height balance with O(1) pointer rotations.",
                "misconceptions": [
                    "Myth: Rotations rearrange the values in arbitrary orders. (Truth: Rotations preserve the exact in-order sequence; the sorted order never changes)."
                ],
                "questions": [
                    {
                        "id": "q_avl_1",
                        "difficulty": "Easy",
                        "question": "What are the only permitted Balance Factors for any node in a valid AVL tree?",
                        "options": [
                            "-1, 0, and +1",
                            "-2, 0, and +2",
                            "Strictly 0 only",
                            "Any positive integer"
                        ],
                        "correct_index": 0,
                        "explanation": "By definition, an AVL tree requires that for every node, the height difference between left and right subtrees differs by at most 1, meaning {-1, 0, +1}.",
                        "hint_tier_1": "AVL balance allows at most a single level of height difference.",
                        "hint_tier_2": "If the difference reaches 2 or -2, an immediate rotation is triggered.",
                        "hint_tier_3": "Allowed set: {-1, 0, +1}.",
                        "worked_example": "Height(L)=2, Height(R)=1 -> BF = +1 (Valid). Height(L)=3, Height(R)=1 -> BF = +2 (Violation, must rotate)."
                    },
                    {
                        "id": "q_avl_2",
                        "difficulty": "Hard",
                        "question": "Which combination of rotations is required to rebalance an AVL tree when an insertion occurs in the Left subtree of a Right child (the RL case)?",
                        "options": [
                            "Single Left Rotation",
                            "Right Rotation on the child, then Left Rotation on the parent",
                            "Left Rotation on the child, then Right Rotation on the parent",
                            "Two consecutive Right Rotations"
                        ],
                        "correct_index": 1,
                        "explanation": "In an RL imbalance, the inner grandchild creates a zigzag. First perform a Right rotation on the right child to straighten it into RR, then perform a Left rotation on the parent.",
                        "hint_tier_1": "A zigzag imbalance requires two steps: first straighten, then balance.",
                        "hint_tier_2": "For Right-Left: first rotate Right on the right child.",
                        "hint_tier_3": "Step 1: Right rotate child. Step 2: Left rotate parent.",
                        "worked_example": "Parent 10, Right child 30, Left grandchild 20. Right rotate 30 -> 10-20-30 (RR). Left rotate 10 -> Root 20 with children 10 and 30."
                    }
                ]
            }
        ]
    },
    {
        "subject": "Computer Architecture",
        "topic_name": "Instruction Pipelining & Hazards",
        "description": "Understand instruction-level parallelism, pipeline stages (IF, ID, EX, MEM, WB), and solving structural, data, and branch hazards.",
        "difficulty_level": "intermediate",
        "concepts": [
            {
                "id": "ca_pipe_1",
                "title": "Classic 5-Stage RISC Pipeline",
                "difficulty_level": "basic",
                "simple_explanation": "Instruction pipelining overlaps the execution of multiple instructions like an automotive assembly line. While one instruction is writing back results, the next is accessing memory, another is executing in the ALU, another is decoding registers, and another is being fetched.",
                "important_points": [
                    "5 standard stages: IF (Fetch), ID (Decode), EX (Execute), MEM (Memory), WB (Write-back).",
                    "Under ideal conditions, throughput approaches 1 Instruction Per Cycle (CPI = 1).",
                    "Pipelining does NOT reduce the latency of a single instruction; it increases overall throughput.",
                    "Clock cycle length is bounded by the slowest individual stage."
                ],
                "visual_representation": """
Clock Cycle:   1    2    3    4    5    6    7
Inst 1:       [IF] [ID] [EX] [MEM][WB]
Inst 2:            [IF] [ID] [EX] [MEM][WB]
Inst 3:                 [IF] [ID] [EX] [MEM][WB]
""",
                "real_world_analogy": "Doing laundry: Washer (45m), Dryer (45m), Folding (45m). Instead of waiting 135 minutes per load before washing the next load, put Load 2 in the washer while Load 1 is drying!",
                "concrete_example": "Without pipelining, 100 instructions taking 5 cycles each = 500 clock cycles. With an ideal 5-stage pipeline, 100 instructions finish in 5 + 99 = 104 clock cycles (~5x speedup!).",
                "key_takeaway": "Pipelining maximizes hardware utilization and instruction throughput by overlapping distinct execution phases.",
                "misconceptions": [
                    "Myth: Pipelining makes an individual instruction complete faster. (Truth: Each instruction still takes 5 clock cycles; but multiple instructions complete in parallel)."
                ],
                "questions": [
                    {
                        "id": "q_pipe_1",
                        "difficulty": "Easy",
                        "question": "What is the primary benefit of instruction pipelining in a modern CPU?",
                        "options": [
                            "It reduces the latency of executing a single isolated instruction",
                            "It increases overall instruction execution throughput per unit of time",
                            "It decreases the physical size of RAM modules",
                            "It eliminates the need for an Arithmetic Logic Unit (ALU)"
                        ],
                        "correct_index": 1,
                        "explanation": "Pipelining overlaps the execution stages of successive instructions, increasing throughput (instructions completed per second) without decreasing individual instruction latency.",
                        "hint_tier_1": "Think about the laundry analogy.",
                        "hint_tier_2": "Throughput vs individual latency.",
                        "hint_tier_3": "It completes more total work per second by keeping all stages busy.",
                        "worked_example": "One car takes 2 hours on assembly line. But a finished car rolls off the line every 2 minutes."
                    },
                    {
                        "id": "q_pipe_2",
                        "difficulty": "Medium",
                        "question": "In a 5-stage pipeline with no stalls, how many clock cycles are required to complete 10 independent instructions from start to finish?",
                        "options": [
                            "50 cycles",
                            "14 cycles",
                            "10 cycles",
                            "5 cycles"
                        ],
                        "correct_index": 1,
                        "explanation": "The first instruction takes 5 cycles to fill the pipeline. Each subsequent instruction completes on each subsequent clock cycle: 5 + (10 - 1) = 14 cycles.",
                        "hint_tier_1": "Formula: Cycles = K stages + (N instructions - 1).",
                        "hint_tier_2": "5 cycles for the first instruction + 9 remaining cycles.",
                        "hint_tier_3": "5 + 9 = 14 cycles.",
                        "worked_example": "Cycles: Inst 1 finishes at cycle 5. Inst 2 at 6... Inst 10 at cycle 14."
                    }
                ]
            },
            {
                "id": "ca_pipe_2",
                "title": "Pipeline Hazards & Data Forwarding",
                "difficulty_level": "advanced",
                "simple_explanation": "Hazards prevent the next instruction from executing in its designated clock cycle. Structural hazards arise from resource conflicts; Data hazards arise when an instruction depends on the result of a prior instruction that hasn't finished; Control hazards arise from branch decisions.",
                "important_points": [
                    "Data hazard: Read-After-Write (RAW) is the most common true data dependency.",
                    "Hardware Data Forwarding (Bypassing) passes computed ALU results directly to the next instruction's EX stage without waiting for memory write-back (WB).",
                    "Load-Use hazard: Even with forwarding, loading from RAM takes time and requires 1 stall bubble.",
                    "Branch prediction reduces control hazard stall penalties."
                ],
                "visual_representation": """
Instruction 1: ADD R1, R2, R3  [IF][ID][EX]--------+ (Result ready at end of EX!)
                                          | Forward directly!
Instruction 2: SUB R4, R1, R5      [IF][ID][EX]<---+ (Needs R1 here)
Without forwarding: Must wait until Inst 1 finishes WB (stalling 2 cycles).
""",
                "real_world_analogy": "Passing a tool on a construction site. Instead of putting the hammer back into the tool shed, locking it up, and having the next worker fetch it, worker A hands the hammer directly to worker B.",
                "concrete_example": "ADD R1, R2, R3 computes R1 in stage EX. SUB R4, R1, R5 needs R1 in its own EX stage on the very next cycle. Forwarding multiplexers route the output of the ALU back into the ALU inputs.",
                "key_takeaway": "Data forwarding resolves RAW hazards in arithmetic instructions with zero stalls by tapping internal pipeline registers.",
                "misconceptions": [
                    "Myth: Data forwarding eliminates all stalls in all programs. (Truth: A Load instruction followed immediately by a dependent instruction still requires a 1-cycle stall because data isn't available until the MEM stage)."
                ],
                "questions": [
                    {
                        "id": "q_haz_1",
                        "difficulty": "Medium",
                        "question": "What type of data hazard occurs when an instruction attempts to read a register before a previous instruction has written to it?",
                        "options": [
                            "Read-After-Write (RAW)",
                            "Write-After-Read (WAR)",
                            "Write-After-Write (WAW)",
                            "Structural Conflict"
                        ],
                        "correct_index": 0,
                        "explanation": "RAW (Read-After-Write) is a true data dependency where Instruction J needs the value produced by Instruction I.",
                        "hint_tier_1": "The older instruction Writes; the newer instruction Reads.",
                        "hint_tier_2": "The newer instruction is Reading After a Write.",
                        "hint_tier_3": "RAW is the classic true data hazard.",
                        "worked_example": "Inst 1: ADD R1, R2, R3 (writes R1). Inst 2: SUB R4, R1, R5 (reads R1)."
                    },
                    {
                        "id": "q_haz_2",
                        "difficulty": "Hard",
                        "question": "Can hardware data forwarding completely eliminate pipeline stalls for a LOAD instruction followed immediately by an ALU instruction that uses the loaded value?",
                        "options": [
                            "Yes, forwarding eliminates all stalls with zero bubble cycles",
                            "No, at least one stall (bubble) is still required because data is only available after the MEM stage",
                            "Yes, by running the CPU clock backwards",
                            "No, it requires 5 full stalls"
                        ],
                        "correct_index": 1,
                        "explanation": "In a Load-Use hazard, the loaded data is only retrieved from cache/memory at the end of the MEM stage. The ALU instruction needs it at the start of EX, creating a 1-cycle time paradox that requires 1 stall bubble.",
                        "hint_tier_1": "At what stage does a LOAD instruction actually have the data from RAM?",
                        "hint_tier_2": "Data from RAM is only ready at the end of MEM stage, which is 1 cycle too late for the next EX stage.",
                        "hint_tier_3": "1 stall bubble is mandatory for load-use with forwarding.",
                        "worked_example": "Inst 1: LW R1, 0(R2) [MEM finishes at t=4]. Inst 2: ADD R3, R1, R4 [EX needs R1 at t=3]. Time paradox! Requires 1 stall."
                    }
                ]
            }
        ]
    },
    {
        "subject": "C++",
        "topic_name": "Exception Handling & RAII",
        "description": "Robust error handling in modern C++, stack unwinding semantics, exception safety guarantees, and the RAII paradigm.",
        "difficulty_level": "intermediate",
        "concepts": [
            {
                "id": "cpp_ex_1",
                "title": "Exception Basics & Stack Unwinding",
                "difficulty_level": "basic",
                "simple_explanation": "Exceptions in C++ separate error detection from error handling. When an anomaly is detected, code calls 'throw'. The runtime performs 'stack unwinding', automatically destroying local objects in reverse order of construction until a matching 'catch' block is found.",
                "important_points": [
                    "Keywords: try, catch, and throw.",
                    "During stack unwinding, destructors of all fully constructed automatic (stack) objects are guaranteed to run.",
                    "If an exception is thrown from a destructor during stack unwinding, std::terminate() is called immediately.",
                    "Catching by const reference (const std::exception&) prevents object slicing."
                ],
                "visual_representation": """
call_func3() ---> throw std::runtime_error("File missing")
   |
   | [Stack Unwinding: destroys local vars in func3]
   v
call_func2() ---> [Stack Unwinding: destroys local vars in func2]
   |
   v
main()       ---> try { ... } catch (const std::exception& e) { HANDLE! }
""",
                "real_world_analogy": "An emergency stop button in a factory. If a machine malfunctions, the system halts the current station, safely shuts down and resets every intermediate assembly station along the conveyor, and notifies the supervisor.",
                "concrete_example": "try {\\n    if (val < 0) throw std::invalid_argument(\"Negative val\");\\n} catch (const std::invalid_argument& e) {\\n    std::cerr << e.what() << std::endl;\\n}",
                "key_takeaway": "Stack unwinding provides guaranteed destructor execution, making clean resource management possible even amidst unexpected errors.",
                "misconceptions": [
                    "Myth: Catching an exception by value (catch (std::exception e)) is standard practice. (Truth: Always catch by const reference to avoid object slicing of derived exception classes)."
                ],
                "questions": [
                    {
                        "id": "q_cpp_1",
                        "difficulty": "Easy",
                        "question": "What happens to local stack variables during stack unwinding when an unhandled exception propagates up the call stack?",
                        "options": [
                            "They remain allocated in memory forever causing leaks",
                            "Their destructors are called automatically in reverse order of construction",
                            "Their values are copied to the global heap",
                            "They are immediately zeroed out without calling destructors"
                        ],
                        "correct_index": 1,
                        "explanation": "C++ guarantees that during stack unwinding, the destructors for all fully constructed stack-allocated objects are executed in reverse order.",
                        "hint_tier_1": "Think about how C++ manages object lifetimes on the stack.",
                        "hint_tier_2": "Destructors are invoked automatically for stack objects.",
                        "hint_tier_3": "Reverse order of construction ensures dependent objects clean up safely.",
                        "worked_example": "Object A created, then Object B. When exception throws, B's destructor runs, then A's destructor runs."
                    },
                    {
                        "id": "q_cpp_2",
                        "difficulty": "Medium",
                        "question": "Why should C++ exceptions always be caught by const reference (catch (const std::exception& e)) rather than by value?",
                        "options": [
                            "To make the program compile faster",
                            "To prevent object slicing and avoid unnecessary object copying",
                            "Because references are stored in CPU registers",
                            "Because value catch is deprecated in C++11"
                        ],
                        "correct_index": 1,
                        "explanation": "Catching by value slices away derived class members (e.g. catching std::runtime_error as std::exception) and triggers unnecessary copy constructor calls.",
                        "hint_tier_1": "What happens when a derived class object is assigned to a base class variable by value?",
                        "hint_tier_2": "Object slicing strips the derived methods and variables.",
                        "hint_tier_3": "Const reference preserves polymorphic identity and avoids copies.",
                        "worked_example": "throw CustomException(\"err\"); catch (std::exception e) slices off CustomException specific data! catch (const std::exception& e) preserves it."
                    }
                ]
            },
            {
                "id": "cpp_ex_2",
                "title": "RAII (Resource Acquisition Is Initialization)",
                "difficulty_level": "intermediate",
                "simple_explanation": "RAII is the core idiom of modern C++: tie the lifetime of a resource (heap memory, file handles, mutex locks, network sockets) to the lifetime of a stack object. Acquire the resource in the constructor, and release it in the destructor.",
                "important_points": [
                    "With RAII, resources are never leaked even if an exception is thrown.",
                    "Standard library smart pointers (std::unique_ptr, std::shared_ptr) are canonical examples of RAII.",
                    "std::lock_guard and std::unique_lock manage mutex synchronization via RAII.",
                    "Never write raw delete or close() calls when an RAII wrapper can manage ownership."
                ],
                "visual_representation": """
Constructor:  std::unique_ptr<File> f(new File("data.txt"));  [Acquire File Handle]
                     |
                Normal work or EXCEPTION thrown!
                     |
Destructor:   f goes out of scope -> ~unique_ptr() called -> close(file) [Guaranteed!]
""",
                "real_world_analogy": "A hotel keycard with an automated checkout timer. When your checkout time arrives, the door locks and charges end automatically; you don't depend on remembering to physically hand the key back to a front desk agent.",
                "concrete_example": "void process() {\\n    std::lock_guard<std::mutex> lock(my_mutex); // acquires mutex\\n    risky_operation(); // even if this throws, mutex is unlocked automatically!\\n}",
                "key_takeaway": "RAII makes exception-safe programming natural by binding resource lifetime to deterministic object destruction.",
                "misconceptions": [
                    "Myth: RAII is only for memory management. (Truth: RAII applies to ANY resource: files, database transactions, mutexes, socket connections, OpenGL textures)."
                ],
                "questions": [
                    {
                        "id": "q_raii_1",
                        "difficulty": "Easy",
                        "question": "What is the primary guarantee provided by the RAII (Resource Acquisition Is Initialization) idiom in C++?",
                        "options": [
                            "Variables are initialized to zero by default",
                            "Acquired resources are guaranteed to be released when the wrapper object goes out of scope",
                            "Compilation speed is doubled",
                            "Pointers can never be null"
                        ],
                        "correct_index": 1,
                        "explanation": "RAII binds resource cleanup to object destruction. When the stack object leaves scope (normally or via exception), its destructor cleans up the resource.",
                        "hint_tier_1": "Think about what happens in the destructor.",
                        "hint_tier_2": "The destructor automatically frees the resource.",
                        "hint_tier_3": "Scope exit guarantees resource release.",
                        "worked_example": "std::unique_ptr<int> p(new int(5)); When function ends, delete is called automatically."
                    },
                    {
                        "id": "q_raii_2",
                        "difficulty": "Hard",
                        "question": "Which level of exception safety guarantee ensures that an operation either succeeds completely or has zero observable side effects (rolling back to the original state)?",
                        "options": [
                            "Basic Guarantee",
                            "Strong Guarantee (Commit-or-Rollback)",
                            "No-throw (nothrow) Guarantee",
                            "Weak Guarantee"
                        ],
                        "correct_index": 1,
                        "explanation": "The Strong Exception Guarantee ensures transactional semantics: if an exception is thrown, program state remains exactly as it was before the operation was called.",
                        "hint_tier_1": "Think of database transactions: ACID commit or rollback.",
                        "hint_tier_2": "Strong guarantee = transactional commit or rollback.",
                        "hint_tier_3": "Basic = no leaks; Strong = rollback; Nothrow = never throws.",
                        "worked_example": "std::vector::push_back provides strong exception safety: if reallocation throws bad_alloc, the original vector is unchanged."
                    }
                ]
            }
        ]
    }
]
