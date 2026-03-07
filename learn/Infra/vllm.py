from collections import deque


class Request:
    def __init__(self, prompt: str, max_new_tokens: int):
        self.prompt = prompt
        self.max_new_tokens = max_new_tokens
        self.generated = []
        self.finished = False

    def step(self):
        if self.finished:
            return

        next_token = str(len(self.generated) + 1)
        self.generated.append(next_token)

        if len(self.generated) >= self.max_new_tokens:
            self.finished = True

    def text(self):
        return self.prompt + " " + " ".join(self.generated)


class NaiveServer:
    def handle(self, requests):
        print("=== Naive server ===")
        print("Process one request completely, then move to the next.\n")

        for i, req in enumerate(requests, start=1):
            print(f"Start request {i}: {req.prompt!r}")
            while not req.finished:
                req.step()
                print(f"  request {i} generated token -> {req.generated[-1]}")
            print(f"Done request {i}: {req.text()}\n")


class SimpleVLLMServer:
    def handle(self, requests):
        print("=== Simple vLLM-style server ===")
        print("Keep all active requests in one batch and generate 1 token for each per round.\n")

        active = deque(requests)
        round_id = 1

        while active:
            batch_size = len(active)
            print(f"Round {round_id}: batch_size={batch_size}")

            for _ in range(batch_size):
                req = active.popleft()
                req.step()
                print(
                    f"  prompt={req.prompt!r} -> generated token {req.generated[-1]}"
                )

                if req.finished:
                    print(f"    finished: {req.text()}")
                else:
                    active.append(req)

            print()
            round_id += 1


def make_requests():
    return [
        Request("Hello", 3),
        Request("How are you", 5),
        Request("Tell me a joke", 2),
    ]


def main():
    naive_requests = make_requests()
    NaiveServer().handle(naive_requests)

    print("-" * 60)

    vllm_requests = make_requests()
    SimpleVLLMServer().handle(vllm_requests)

    print("=== Main idea ===")
    print("1. Real LLM generation is still one token at a time.")
    print("2. vLLM improves throughput by serving many requests together.")
    print("3. When one request finishes, others keep using the batch.")
    print("4. In the real system, KV cache management makes this efficient.")


if __name__ == "__main__":
    main()
