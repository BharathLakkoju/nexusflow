import Link from "next/link";

const FOOTER_LINKS = {
  Product: [
    { href: "/features", label: "Features" },
    { href: "/services", label: "Services" },
    { href: "/dashboard", label: "Dashboard" },
  ],
  Company: [
    { href: "/about", label: "About" },
    { href: "/", label: "Blog" },
    { href: "/", label: "Careers" },
  ],
  Legal: [
    { href: "/", label: "Privacy" },
    { href: "/", label: "Terms" },
    { href: "/", label: "Security" },
  ],
};

export function MarketingFooter() {
  return (
    <footer className="bg-brown-900 text-brown-200">
      <div className="max-w-[1400px] mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="h-8 w-8 rounded-lg bg-brown-600 flex items-center justify-center">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  className="h-4 w-4 text-brown-100"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
                  />
                </svg>
              </div>
              <span className="text-lg font-700 text-brown-50 tracking-tight">
                NexusFlow
              </span>
            </div>
            <p className="text-sm text-brown-400 leading-relaxed max-w-[200px]">
              Multi-agent AI orchestration for teams that move fast.
            </p>
          </div>

          {/* Links */}
          {Object.entries(FOOTER_LINKS).map(([category, links]) => (
            <div key={category}>
              <h4 className="text-xs font-semibold tracking-widest uppercase text-brown-500 mb-4">
                {category}
              </h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-brown-400 hover:text-brown-200 transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-14 pt-6 border-t border-brown-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-brown-600">
            &copy; {new Date().getFullYear()} NexusFlow AI. All rights reserved.
          </p>
          <p className="text-xs text-brown-600">
            Built with purpose for AI-native teams.
          </p>
        </div>
      </div>
    </footer>
  );
}
