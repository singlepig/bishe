#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>


int main()
{
    // read an image
    cv::Mat image = cv::imread("../lena.jpg");
    // create image window named "my image"
    cv::namedWindow("my image");
    // show the image on window;
    cv::imshow("my image", image);
    // wait key
    cv::waitKey(0);

    return 1;
}
