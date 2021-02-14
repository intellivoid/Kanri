# Kanri

Kanri is a Pyrogram-based, modal, performant and scalable Telegram group management bot software. 

`Copyright (C) 2020-2021 Intellivoid Technologies.`
 
## Useful links
  - [Kanri Support](https://t.me/KanriGroup)
  - [Kanri Update Channel](https://t.me/KanriUpdates)
  - [Intellivoid](https://t.me/Intellivoid)
  - [Intellivoid Discussions](https://t.me/IntellivoidDiscussions)
  - [Intellivoid Community](https://t.me/IntellivoidCommunity)

If you want to join our group chats, **we advise that you read the rules carefully**
before participating in them.


-------------------------------------------------------------------------------------


## Modules

- Modules are automatically loaded from the `modules` folder, so just 
  put your `.py` file in there and you're good to go!

- Mention the module you wanna load in `LOAD` and the module don't wanna 
  load in `NOLOAD`, keep both empty to load all modules from `modules` directory.


-------------------------------------------------------------------------------------

## Branch purposes

Kanri will have multiple branches for different purposes, these are the
main branches you should understand before contributing to this project.

 - `production` This is the production branch that the server will listen to and
    will use to deploy Kanri in production. This is the most stable branch, and it's
    ready for production. **We do not push experimental or patches to this branch
    until we can confirm that it's stable for production**
 
 - `master` This is the next thing to production in terms of stable, here this is
    where all new changes are pushed before they are merged into the production
    branch. This is like the testing branch where we would run in test
    environment to double check before pushing to production. Everything pushed to
    this branch must be stable and finished.
   
Any other branches should be treated as work in progress features that is currently
being worked on to release to production.

## Contributing to the project
 - You must sign off on your commit.
 - You must sign the commit via GPG Key.
 - Make sure your PR passes all CI.