import { BrandMark } from "@/components/welcome/brand-mark"

export function SiteFooter() {
  return (
    <footer className="border-t border-line py-14 pb-10">
      <div className="mx-auto max-w-[1140px] px-7">
        <div className="mb-9 flex flex-wrap justify-between gap-10">
          <div>
            <div className="flex items-center gap-[9px] text-[15px] font-semibold">
              <BrandMark />
              <span>
                VinUni AI Thực Chiến
                <span className="mx-0.5 font-normal text-ink-soft">·</span>
              </span>
              <small className="text-[12.5px] font-medium text-ink-soft">
                VLearn
              </small>
            </div>
            <p className="mt-2.5 max-w-[280px] text-sm text-ink-soft">
              Nền tảng học thích ứng dành cho cộng đồng VinUni AI Thực Chiến.
            </p>
          </div>

          <div className="flex flex-wrap gap-16">
            <div>
              <h4 className="mb-3 text-[12.5px] font-semibold tracking-[0.05em] text-ink-soft uppercase">
                Sản phẩm
              </h4>
              <a
                href="#daily-loop"
                className="mb-2 block text-[14.5px] text-ink hover:text-maroon"
              >
                Cách học
              </a>
              <a
                href="#features"
                className="mb-2 block text-[14.5px] text-ink hover:text-maroon"
              >
                Tính năng
              </a>
            </div>
            <div>
              <h4 className="mb-3 text-[12.5px] font-semibold tracking-[0.05em] text-ink-soft uppercase">
                Truy cập
              </h4>
              <a
                href="#"
                className="mb-2 block text-[14.5px] text-ink hover:text-maroon"
              >
                Đăng nhập
              </a>
              <a
                href="#"
                className="mb-2 block text-[14.5px] text-ink hover:text-maroon"
              >
                Hỗ trợ
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-line pt-5.5 text-[13px] text-ink-soft">
          © 2026 VLearn · VinUni AI Thực Chiến. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
