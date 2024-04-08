def scorer(l,g):
    assert len(l) == len(g), "Original and target inputs must be of same size."
    scores = []
    for i in range(len(l)):
        u_mic = 0
        l_mic = 0
        s = l[i]
        if len(s) != len(g[i]):
            print("Original and target sentence not of same length")
            break
        for j in range(len(s)):
            if s[j]['head'] == g[i][j]['head']:
                u_mic += 1
                if s[j]['deprel'] == g[i][j]['deprel']:
                    l_mic += 1
        uas = u_mic/len(s)
        las = l_mic/len(s)
        scores.append((uas,las))
    return scores