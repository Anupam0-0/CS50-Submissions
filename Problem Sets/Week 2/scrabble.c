#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>

// Points acc. to alphabets
int POINTS[] = {1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10};
int score(string w);
void compare(int a, int b);

int main()
{
    string word1 = get_string("Player 1: ");
    string word2 = get_string("Player 2: ");

    int score1 = score(word1);
    int score2 = score(word2);

    compare(score1, score2);
}

void compare(int a, int b)
{
    if (a > b)
        printf("Player 1 wins!\n");
    if (a < b)
        printf("Player 2 wins!\n");
    else
        printf("Tie!\n");
}

int score(string w)
{
    int len = 0, res = 0;
    len = strlen(w);

    for (int i = 0; i < len; i++)
    {
        char word = toupper(w[i]);
        if (isupper(word))
            res += POINTS[word - 65];
        else
            continue;
    }
    return res;
}
