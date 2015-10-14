
#include <gmock/gmock.h>
#include <gtest/gtest.h>
using testing::AtLeast;

class ITurtle {
public:
    virtual ~ITurtle() {}
    virtual void PenDown() = 0;
};

class Painter {
    ITurtle* turtle;

public:
    Painter(ITurtle* turtle)
        : turtle(turtle)
    {
    }

    bool DrawCircle(double x, double y, double r) {
        turtle -> PenDown();
        return true;
    }
};

struct MockTurtle : public ITurtle
{
    MOCK_METHOD0(PenDown, void());
};

TEST(PainterTest, CanDrawSomething) {
    MockTurtle turtle;
    EXPECT_CALL(turtle, PenDown())
        .Times(AtLeast(1));

    Painter painter(&turtle);
    EXPECT_TRUE(painter.DrawCircle(0, 0, 10));
}

