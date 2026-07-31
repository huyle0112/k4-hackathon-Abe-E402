const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "")

export class ApiError extends Error {
  readonly status?: number

  constructor(
    message: string,
    status?: number
  ) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

export async function postJson<T>(
  path: string,
  body: unknown,
  headers?: HeadersInit
): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...headers },
      body: JSON.stringify(body),
    })
  } catch {
    throw new ApiError(
      `Không thể kết nối API tại ${API_BASE_URL}. Hãy kiểm tra backend đang chạy.`
    )
  }

  if (!response.ok) {
    let detail = `API trả về lỗi ${response.status}.`
    try {
      const payload = (await response.json()) as { detail?: unknown }
      if (typeof payload.detail === "string") detail = payload.detail
    } catch {
      // Keep the HTTP status message when the response is not JSON.
    }
    throw new ApiError(detail, response.status)
  }

  return (await response.json()) as T
}
