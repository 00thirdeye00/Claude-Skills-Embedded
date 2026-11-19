# Stack sizing and schedulability analysis

## Contents
- Stack sizing
- Utilization bound
- Response-time analysis
- Worked example
- Common failure patterns

## Stack sizing

1. Start from the deepest call chain of the task, including library calls such as formatted printing, which can use hundreds of bytes.
2. Add the exception frame the hardware pushes on interrupt entry: 32 bytes for a basic frame, 104 bytes when the FPU extended frame is used on cores with an FPU.
3. On Cortex-M kernels, add the context-switch save area (callee-saved registers, plus the upper FPU registers if the task uses floating point).
4. Measure with a high-water mark API on target under worst-case load, then add 20 to 30 percent margin.
5. Compiler help: `-fstack-usage` gives per-function stack use; `-Wstack-usage=<bytes>` warns on large frames. Recursion and function pointers need manual analysis.
6. Check units: some kernels count stack depth in words, others in bytes.

Interrupt handlers run on the main stack in typical Cortex-M kernel ports, so size the main stack for the deepest nest of interrupts.

## Utilization bound

For `n` independent periodic tasks with rate-monotonic priorities:

```
U = sum(Ci / Ti)   must be   <=   n * (2^(1/n) - 1)
```

The bound is about 0.828 for two tasks, 0.780 for three, and approaches 0.693 as `n` grows. Passing the bound guarantees schedulability under the usual assumptions (independent tasks, deadline equals period). Failing it does not prove failure; use response-time analysis.

## Response-time analysis

For task `i`, iterate until `R` stops changing:

```
R = Ci + Bi + sum over higher-priority tasks j of ceil(R / Tj) * Cj
```

`Bi` is the longest time a lower-priority task can block task `i` (a critical section under a priority-inheritance mutex, or interrupts-masked time). The task meets its deadline if `R <= Di`. Add interrupt service time as extra high-priority load.

## Worked example

| Task | C | T | Priority |
|---|---|---|---|
| A | 1 ms | 5 ms | High |
| B | 2 ms | 10 ms | Medium |
| C | 4 ms | 20 ms | Low |

Utilization: 0.2 + 0.2 + 0.2 = 0.6, below the 0.780 bound, so the set is schedulable.

Response time for C with no blocking: start at R = 4. Then R = 4 + ceil(4/5)*1 + ceil(4/10)*2 = 7. Then R = 4 + ceil(7/5)*1 + ceil(7/10)*2 = 8. Then R = 4 + ceil(8/5)*1 + ceil(8/10)*2 = 8. It converges at 8 ms, within the 20 ms deadline.

## Common failure patterns

| Pattern | Symptom | Remedy |
|---|---|---|
| Priority inversion | A high-priority task stalls behind a medium task that preempts a low-priority lock holder | Mutex with priority inheritance or ceiling; shorten critical sections |
| Deadlock | Two tasks wait on each other's locks | Global lock order; timeouts on lock acquisition |
| Starvation | A low-priority task never runs | Add idle margin; avoid busy-waiting at high priority |
| Queue overflow | Lost messages under burst | Size queues from worst-case burst; report overruns |
| Stack overflow | Random corruption, faults | High-water-mark monitoring; overflow hook; MPU guard where available |
| Heap fragmentation | Allocation fails after long runtime | Static allocation, or a pool allocator with fixed block sizes |
| Missed tick or coarse delays | Jitter in periodic tasks | Use absolute-time delay APIs for periodic tasks |
