#include <cs50.h>
#include <stdio.h>

int main()
{
    string str = get_string("What's your name?\n");
    printf("hello, %s\n", str);
}
