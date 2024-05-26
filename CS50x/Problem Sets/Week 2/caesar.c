#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, string argv[])
{
    if (argc != 2)
    { // for one command-line arg.
        printf("Usage: ./caesar key\n");
        return 1;
    }

    // check that the input is a digit
    for (int i = 0; i < strlen(argv[1]); i++)
    {
        if (!isdigit(argv[1][i]))
        {
            printf("Usage: ./caesar key\n");
            return 1;
        }
    }

    // input from user
    string txt = get_string("plaintext: ");

    // encyrption
    int k = atoi(argv[1]);
    printf("ciphertext: ");

    // conversion part
    for (int i = 0; i < strlen(txt); i++)
    {
        if (isupper(txt[i]))
        {
            printf("%c", (((txt[i] - 65) + k) % 26) + 65);
        }
        else if (islower(txt[i]))
        {
            printf("%c", (((txt[i] - 97) + k) % 26) + 97);
        }
        else
            printf("%c", txt[i]);
    }
    printf("\n");
}
