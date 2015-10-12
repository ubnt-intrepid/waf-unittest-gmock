
#include <gtest/gtest.h>
#include <gmock/gmock.h>

TEST(test,test) {
    int a = 0;
    a++;
    ASSERT_EQ(a, 1);
}

