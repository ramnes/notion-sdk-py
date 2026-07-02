这是合并后的完整最终稿。

---

### English (paste into the issue)

**Quick update:** I prototyped this migration on a local branch and ran the full test suite against it. Here's how each of the concerns I listed above played out:

**1. Test infrastructure — solved.** `vcrpy` 8.2.0 added native `httpx2` support: it intercepts `httpx2`'s transports (`HTTPTransport.handle_request` / `AsyncHTTPTransport.handle_async_request`) directly. The **existing cassettes replay unchanged** — no re-recording or matcher changes needed, since cassettes record at the HTTP level and the recordings are decoupled from the client library. The only test-side change is bumping `vcrpy==8.2.0` in `requirements/tests.txt`.

**2. Code change — mechanical.** `httpx2` is API-compatible: `Client`, `AsyncClient`, `Request`, `Response`, `Headers`, `URL`, `Timeout`, `HTTPStatusError`, `TimeoutException` are all present with the same interface, so it's essentially a rename of imports and references in `client.py` / `errors.py`. (I also dropped the `typing_extensions` fallback for `TypeGuard`, since it's in stdlib `typing` from 3.10 on.)

**3. Python floor — bumped to 3.10.** Both `httpx2` and `vcrpy` 8.2.0 require 3.10+, so this is unavoidable: `python_requires>=3.10`, drop 3.8/3.9 from the classifiers and the CI matrix.

**4. The one genuine breaking change to decide on:** the public API where users pass their own client. `Client` / `AsyncClient` now expect an `httpx2.Client` / `AsyncClient` for that optional argument, so anyone currently passing a plain `httpx.Client` would have to switch. My recommendation is a clean switch to `httpx2` rather than supporting both — keeping both would drag two HTTP stacks (`httpcore` + `httpcore2`) into every downstream dependency tree for little benefit, and it's the same path Starlette/FastAPI took. This breaking change (plus the 3.10 floor) is better handled with a clear major/minor version bump + a changelog note than with dual-stack compatibility.

With those in place, the full test suite passes locally (191 tests). I haven't opened a PR yet — I wanted to check first whether you're open to this direction (and the breaking-change/timing implications) before putting one together. Happy to open it if you'd like.

---

### 中文参考

> **进展更新:** 我在本地分支上做了迁移原型并跑通了整套测试。针对我上面列的几个顾虑,结论如下:
>
> **1. 测试基础设施 — 已解决。** `vcrpy` 8.2.0 原生支持了 `httpx2`,会直接拦截 `httpx2` 的传输层(`HTTPTransport.handle_request` / `AsyncHTTPTransport.handle_async_request`)。**现有 cassette 无需改动即可回放**,不需要重录、也不用改 matcher——因为 cassette 记录的是 HTTP 层交换,与具体客户端库解耦。测试侧唯一的改动是把 `requirements/tests.txt` 里的 vcrpy 升到 `8.2.0`。
>
> **2. 代码改动 — 纯机械替换。** `httpx2` API 兼容:`Client`、`AsyncClient`、`Request`、`Response`、`Headers`、`URL`、`Timeout`、`HTTPStatusError`、`TimeoutException` 都在,接口一致,基本就是把 `client.py` / `errors.py` 里的 import 和引用改个名。(顺带去掉了 `TypeGuard` 的 `typing_extensions` 兼容分支,因为 3.10 起它已进 stdlib 的 `typing`。)
>
> **3. Python 最低版本 — 提到 3.10。** `httpx2` 和 vcrpy 8.2.0 都要求 3.10+,这点绕不开:`python_requires>=3.10`,classifiers 和 CI matrix 去掉 3.8/3.9。
>
> **4. 唯一需要拍板的破坏性改动:** 用户自带 client 的那个公开 API。`Client` / `AsyncClient` 的那个可选参数现在期望传入 `httpx2.Client` / `AsyncClient`,所以目前传普通 `httpx.Client` 的用户需要跟着换。我倾向于干净切到 `httpx2`,而不是两者并存——并存会把 `httpcore` + `httpcore2` 两套 HTTP 栈塞进所有下游依赖树,收益很小,而且 Starlette/FastAPI 走的也是这条路。这个破坏性改动(加上 3.10 下限)用「明确升 major/minor 版本号 + changelog 说明」来处理,比维持双栈兼容要干净得多。
>
> 以上改完后,本地整套测试全部通过(191 个)。我还没提 PR——想先确认你是否认可这个方向(以及破坏性改动/时间节奏的考量),再来准备。如果你愿意,我可以把 PR 提上来。

---

第 4 点已经把「推荐干净切换、反对双栈并存」的表态自然融了进去,既回应了你自己最初列的 API 顾虑,也给出了明确立场和先例支撑。可以直接贴。
