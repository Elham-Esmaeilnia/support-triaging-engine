# vLLM Deployment Considerations for Maximum Throughput

## Hypothetical Question

**If this microservice had to be deployed on our internal server using vLLM, which configuration changes (such as `max_model_len` or `tensor_parallel_size`) would be critical for achieving the highest possible throughput?**

---

## Answer

If this microservice were deployed internally with **vLLM**, the most important configuration choices for maximizing throughput are those that influence:

- GPU memory usage  
- request concurrency  
- batching efficiency  
- model placement across GPUs  

Since this service performs ticket triage, requests are relatively short and responses are small structured JSON outputs. Therefore, the deployment should prioritize high concurrency and efficient batching rather than very large context windows.

---

## 1. `max_model_len`

`max_model_len` determines the maximum number of tokens reserved for each request (input + output). Larger values increase KV-cache memory usage and reduce the number of concurrent requests the GPU can handle.

Because ticket texts are already preprocessed and truncated, very large context windows are unnecessary.

**Recommended setting:**

- `max_model_len = 2048`
- or at most `4096`

This comfortably fits:

- the processed ticket text  
- the system prompt  
- the short JSON response  

Lower context limits reduce KV-cache usage and allow more concurrent sequences, improving throughput.

---

## 2. `tensor_parallel_size`

`tensor_parallel_size` defines how many GPUs are used to serve one model instance. While necessary for very large models, it introduces cross-GPU communication overhead.

Since the company already has **two GPUs (NVIDIA A100 and NVIDIA H200)**, the recommended approach is:

- run two independent vLLM instances  
- set `tensor_parallel_size = 1` on each GPU  

This avoids synchronization overhead and allows each GPU to process requests independently, maximizing overall throughput.

---

## 3. Batching and `max_num_seqs`

`max_num_seqs` controls how many requests can be processed concurrently in a scheduling cycle. Higher values generally increase GPU utilization.

Because the GPUs have different memory capacities, batching should be tuned separately.

**Recommended starting values:**

- **NVIDIA A100:** `max_num_seqs = 16 – 32`  
- **NVIDIA H200:** `max_num_seqs = 48 – 96`  

A practical initial configuration:

- **A100:** `max_num_seqs = 24`  
- **H200:** `max_num_seqs = 64`  

These values should be validated through load testing and adjusted based on the selected model size and observed memory usage.

---

## 4. Model Size Selection

Throughput is also influenced by model size.

For ticket triage, extremely large models are usually unnecessary because the task mainly involves structured classification and summarization.

A suitable deployment choice would be:

- a small or medium instruct model  
- one that fits comfortably on a single GPU  
- one that produces consistent structured outputs  

Models in the 7B–8B range are typically a good balance between accuracy and serving efficiency.

---

## 5. KV Cache Optimization

Additional throughput improvements can come from KV-cache optimization.

Recommended options:

- `kv_cache_dtype = fp8` (preferred when supported)  
- `kv_cache_dtype = bf16` as a fallback  

Reducing KV-cache precision lowers memory usage and increases the number of concurrent sequences the GPU can handle.

---

## Recommended Configuration Summary

For deployment on **A100 + H200**, a practical baseline would be:

- Run two independent vLLM instances (one per GPU)  
- `tensor_parallel_size = 1`  
- `max_model_len = 2048` (up to `4096` on H200 if needed)  
- Tune batching separately:
  - **A100:** ~24 sequences  
  - **H200:** ~64 sequences  
- Use a 7B–8B model that fits on a single GPU  
- Enable memory-efficient KV cache (`fp8` or `bf16`)  

---

## Final Conclusion

For this ticket-triaging microservice, the key deployment principle is:

> Optimize for short-context, high-concurrency inference rather than long-context generation.

This means keeping context windows small, avoiding unnecessary tensor parallelism, and maximizing batching so both GPUs can operate at high utilization.
