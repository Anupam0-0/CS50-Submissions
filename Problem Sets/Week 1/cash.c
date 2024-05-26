#include <cs50.h>
#include <stdio.h>

void factor(int n)
{
    int r1, r2, r3, r4;
    int l1, l2, l3, l4;
    l1 = n / 25;
    r1 = n % 25;
    l2 = r1 / 10;
    r2 = r1 % 10;
    l3 = r2 / 5;
    r3 = r2 % 5;
    l4 = r3 / 1;
    r4 = r3 % 1;
    int total = l1 + l2 + l3 + l4;
    printf("%d\n", total);
}

int main()
{
    int n;
    do
    {
        n = get_int("Change owed: ");
    }
    while (n < 1);
    {
        factor(n);
    }
}
