9/6/19

* First draft 'model' working
    * randomly chooses cards

* Using default drafter, score: 118
* Using random drafter: score: 88

Can now run through games and interact with client

Tomorrow:

Setup Neural net to take in cards and start adding weights?

9/7/19
Notes:
* 75x75 cardmatrix with 1x75 deck matrix output is best cards to add

* card matrix is symmetric
* SGA/SGD? Impurity metrics
* How to optimize finding weights of 75x75 matrix
    * 2850 weights to optimize
    

9/8/19

Business case:
* Games like this live and die on game balance
* MTG case study misbalanced cards
    * huge costs having to reprint/release errata
* Exploration of space with humans problematic
    * unable to fully explore and depends on personal expertise
    
Reinforcement learning
* find degenerate use cases and hopefully nix before they're problematic/printed
* pre-test possible changes
* find playstyles and possibly improve/give feedback on what cards/styles have good/bad winrates