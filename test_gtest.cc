
#include <gtest/gtest.h>
#include <gmock/gmock.h>

TEST(test,test) {
    int a = 0;
    a++;
    ASSERT_EQ(1, a);
}

TEST(test, test_failure) {
    int a = 1;
    ASSERT_EQ(2, a);
}

