import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#EE4D2D",       // Shopee Orange
                primary_dark: "#D03E1E",
                telegram: "#0088cc",      // Telegram Blue
                bg_light: "#FFFFFF",
                text_main: "#333333",
                success: "#28A745",
            },
        },
    },
    plugins: [],
};
export default config;
