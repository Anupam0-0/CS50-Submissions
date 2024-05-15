#include <cs50.h>
#include <stdio.h>

void pattern(int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n - i - 1; j++)
        {
            printf(" ");
        }
        for (int j = 0; j < i + 1; j++)
        {
            printf("#");
        }
        printf("\n");
    }
}

int main()
{
    int n;
    do
    {
        n = get_int("Size: ");
    }
    while (n < 1 || n > 20);
    {
        pattern(n);
    }
}
