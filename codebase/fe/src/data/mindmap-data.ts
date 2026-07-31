import type { MindElixirData, NodeObj } from "mind-elixir"
import { SIDE } from "mind-elixir"

let uid = 0
export function node(topic: string, children?: NodeObj[]): NodeObj {
  uid += 1
  return { id: `n${uid}`, topic, children }
}

function mindmap(rootTopic: string, children: NodeObj[]): MindElixirData {
  return {
    nodeData: { ...node(rootTopic, children), root: true } as NodeObj,
    arrows: [],
    summaries: [],
    direction: SIDE,
  }
}

/**
 * Mock mindmap content keyed by SlideFile.id (see comp2010-slides.ts).
 * Day02's outline mirrors the real d2-slide-hackathon.pdf content; the rest
 * are illustrative placeholders until real slide content is wired in.
 */
export const MINDMAPS: Record<string, MindElixirData> = {
  "D01-S01": mindmap("Giới thiệu môn học · Day 01", [
    node("Mục tiêu môn học", [
      node("Tư duy giải quyết vấn đề bằng AI"),
      node("Xây dựng sản phẩm thực chiến"),
    ]),
    node("Cấu trúc chương trình", [
      node("Phase 1: Xác định bài toán"),
      node("Phase 2: Xây dựng giải pháp"),
      node("Phase 3: Demo & đánh giá"),
    ]),
    node("Quy tắc lớp học", [
      node("Làm việc theo nhóm"),
      node("Nộp bài đúng hạn từng mốc"),
    ]),
    node("Công cụ sử dụng", [node("LLM APIs"), node("Prototyping tools")]),
  ]),

  "D02-S01": mindmap("Xác định bài toán cho AI · Day 02", [
    node("Từ yêu cầu mơ hồ đến Problem Statement rõ ràng"),
    node("Khung lý thuyết (4h)", [
      node("Problem Discovery (Double Diamond, HCD)"),
      node("Problem Statement & định lượng hóa"),
      node("PAIR① AI có thêm giá trị?"),
      node("PAIR② Automate/Augment → Rule/Workflow/Agent"),
      node("PAIR③ Reward function & success criteria"),
    ]),
    node("Thực hành Lab (4h)", [
      node("Tìm 5 bài toán & điền 3 Problem Cards"),
      node("Phản biện chéo, chốt 1 bài toán"),
      node("Viết nhật ký phân tích (Reflection Log)"),
    ]),
    node("Bài nộp cuối buổi", [
      node("Nhật ký tìm và lọc bài toán (Cá nhân)"),
      node("Problem Statement hoàn chỉnh (Nhóm)"),
      node("Nhật ký phản tư (Cá nhân)"),
    ]),
  ]),

  "D03-S01": mindmap("Thiết kế giải pháp AI · Day 03", [
    node("Từ Problem Statement đến giải pháp"),
    node("Kiến trúc giải pháp", [
      node("Rule-based"),
      node("Workflow tự động hoá"),
      node("Agent-based"),
    ]),
    node("Lựa chọn công cụ", [
      node("LLM APIs"),
      node("RAG / Vector DB"),
      node("No-code / Low-code"),
    ]),
    node("Thực hành", [
      node("Vẽ kiến trúc giải pháp"),
      node("Chọn tech stack cho nhóm"),
    ]),
  ]),

  "D04-S01": mindmap("Xây dựng MVP · Day 04", [
    node("Prototype nhanh", [node("Wireframe"), node("Flow người dùng")]),
    node("Tích hợp AI", [
      node("Prompt engineering"),
      node("Xử lý dữ liệu đầu vào / đầu ra"),
    ]),
    node("Kiểm thử", [node("Test case cơ bản"), node("Thu thập phản hồi")]),
    node("Chuẩn bị demo"),
  ]),

  "D05-S01": mindmap("Demo & Đánh giá · Day 05", [
    node("Chuẩn bị trình bày", [
      node("Pitch deck"),
      node("Kịch bản demo"),
    ]),
    node("Tiêu chí đánh giá", [
      node("Tính khả thi"),
      node("Giá trị thực tế"),
      node("Chất lượng kỹ thuật"),
    ]),
    node("Phản hồi & rút kinh nghiệm", [
      node("Điểm mạnh"),
      node("Điểm cần cải thiện"),
    ]),
    node("Bước tiếp theo"),
  ]),
}
