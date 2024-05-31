#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <iostream>
#include <sstream>

#include <lunasvg.h>

#include <windows.h>

using namespace lunasvg;

long svg2png_impl(std::string svg, double width, double height, long bgColor, std::string png, HBITMAP * bmp)
{
    auto document = Document::loadFromFile(svg);
    if (!document) return -1;

    if (height == 0.)
    {
        if (document->width() > 1)
        {
            height = width * document->height() / document->width();
        }
    }
    else if (height == -1.)
    {
        if (width < 0)
        {
            width = -width;
            height = document->height() / width;
            width = document->width() / width;
        }
        else
        {
            height = document->height() * width;
            width = document->width() * width;
        }
    }
    else if ((height < 0) && (width < 0) && (document->width() > 0) && (document->height() > 0))
    {
        // fit into this box
        double targetHeight = -height;
        double targetWidth = -width;
        double targetRatio = targetWidth / targetHeight;
        double docRatio = document->width() / double(document->height());
        if (targetRatio > docRatio)
        {
            height = targetHeight;
            width = height * docRatio;
        }
        else
        {
            width = targetWidth;
            height = width / docRatio;
        }
    }

    auto bitmap = document->renderToBitmap(std::uint32_t(width + 0.5), std::uint32_t(height + 0.5), bgColor);
    if (!bitmap.valid()) return -1;

    if (!png.empty())
    {
        size_t base = svg.find_last_of("/\\") + 1;
        size_t len = svg.length() - base - 4;
        if (png.length() == 0)
        {
            png = svg.substr(base, len);
        }
        len = png.length();
        if ((len < 4) || png.substr(len - 4).compare(".png"))
        {
            png.append(".png");
        }

        bitmap.convertToRGBA();
        stbi_write_png(png.c_str(), int(bitmap.width()), int(bitmap.height()), 4, bitmap.data(), 0);
    }

    if (bmp)
    {
        BITMAP bmpdef;
        bmpdef.bmType = 0;
        bmpdef.bmWidth = bitmap.width();
        bmpdef.bmHeight = bitmap.height();
        bmpdef.bmWidthBytes = bitmap.width() * 4;
        bmpdef.bmPlanes = 1;
        bmpdef.bmBitsPixel = 32;
        bmpdef.bmBits = bitmap.data();
        *bmp = CreateBitmapIndirect(&bmpdef);
    }

    return 0;
}

#ifdef _WINEXE

int help()
{
    std::cout << "lunsgv Samuel Ugochukwu https://github.com/sammycage/lunasvg MIT licensed\n";
    std::cout << "Usage: \n"
                 "   svg2png [filename] [resolution] [bgColor] [png file]\n"
                 "Examples: \n"
                 "   $ svg2png input.svg\n"
                 "   $ svg2png input.svg 512x512\n"
                 "   $ svg2png input.svg 512x512 0xff00ffff\n"
                 "   $ svg2png input.svg 512x 0xff00ffff        (width 512 with original aspect ratio)\n"
                 "   $ svg2png input.svg 1 0xff00ffff           (original size)\n"
                 "   $ svg2png input.svg -2 0xff00ffff          (two times smaller)\n\n";
    return 1;
}

bool setup(int argc, char** argv, std::string& filename, double& width, double& height, std::uint32_t& bgColor, std::string & pngfile)
{
    if(argc > 1) filename.assign(argv[1]);
    if(argc > 2)
    {
        std::stringstream ss;

        ss << argv[2];
        ss >> width;

        if (ss.fail())
        {
            return false;
        } 
        if(ss.get() != 'x')
        {
            // a height of -1 means width is a ratio
            height = -1.;
        }
        else
        {
            ss >> height;
            if (ss.fail())
            {
                // a height of 0 means original aspect ratio
                height = 0;
            }
        }
    }

    if(argc > 3)
    {
        std::stringstream ss;

        ss << std::hex << argv[3];
        ss >> std::hex >> bgColor;
    }

    if (argc > 4)
    {
        pngfile.assign(argv[4]);
    }

    return true;
}

int main(int argc, char** argv)
{
    std::string filename;
    std::string pngname;
    double width = 0, height = 0;
    std::uint32_t bgColor = 0x00000000;
    if(!setup(argc, argv, filename, width, height, bgColor,pngname)) return help();

    if (svg2png_impl(filename, width, height, bgColor, pngname,NULL))
    {
        help();
        return -1;
    }
	std::cout << "Generated PNG file : " << pngname << std::endl;
	return 0;
}

#else

extern "C" __declspec(dllexport) long __cdecl svg2png(const wchar_t* svg, double height, double width, long bgColor, const wchar_t* png)
{
    return svg2png_impl(std::string(svg,svg+wcslen(svg)), height, width, bgColor, std::string(png,png+wcslen(png)),NULL);
}

extern "C" __declspec(dllexport) HBITMAP __cdecl svg2bitmap(const wchar_t* svg, double height, double width, long bgColor)
{
    HBITMAP bmp = NULL;
    svg2png_impl(std::string(svg,svg+wcslen(svg)), height, width, bgColor, std::string(""),&bmp);
    return bmp;
}


#endif
