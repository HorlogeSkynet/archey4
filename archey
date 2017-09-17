#!/usr/bin/env python3
#
# archey4
#
# -- Archey is a simple system information tool written in Python.
#
# Copyright 2010 Melik Manukyan <melik@archlinux.us>
# Copyright 2010 David Vazgenovich Shakaryan <dvshakaryan@gmail.com>
#
# ASCII art by Brett Bohnenkamper <kittykatt@silverirc.com>
# Changes Jerome Launay <jerome@projet-libre.org>
# Fedora support by YeOK <yeok@henpen.org>
# First IP handling by Normand Cyr <normand.cyr@gmail.com>
#
# Currently maintained by Samuel FORESTIER <https://horlogeskynet.github.io/>
#
# This program IS A FORK of
# the original Archey project <https://github.com/djmelik/archey>
#
# Distributed under the terms of the GNU General Public License v3.
# See <http://www.gnu.org/licenses/gpl.txt> for the full license text.


import re

from enum import Enum
from math import floor
from os import getenv, getuid
from subprocess import Popen, PIPE, DEVNULL, check_output, \
                       CalledProcessError, TimeoutExpired


# -------------- Enumerations -------------- #

class Distributions(Enum):
    ARCH_LINUX = 'Arch.*'
    BUNSENLABS = 'BunsenLabs'
    CRUNCHBANG = 'CrunchBang'
    DEBIAN = '(Rasp|De)bian'
    FEDORA = 'Fedora'
    GENTOO = 'Gentoo'
    KALI_LINUX = 'Kali'
    MANJARO_LINUX = 'ManjaroLinux'
    LINUX = 'Linux'
    LINUX_MINT = 'LinuxMint'
    OPENSUSE = 'openSUSE'
    RED_HAT = 'Red Hat'
    UBUNTU = 'Ubuntu'


# -------------- Dictionaries -------------- #

colorDict = {
    Distributions.ARCH_LINUX: ['\x1b[0;34m', '\x1b[1;34m'],
    Distributions.BUNSENLABS: ['\x1b[1;37m', '\x1b[1;33m', '\x1b[0;33m'],
    Distributions.CRUNCHBANG: ['\x1b[1;37m', '\x1b[1;37m'],
    Distributions.DEBIAN: ['\x1b[0;31m', '\x1b[1;31m'],
    Distributions.FEDORA: ['\x1b[1;37m', '\x1b[0;34m'],
    Distributions.GENTOO: ['\x1b[1;37m', '\x1b[1;35m'],
    Distributions.KALI_LINUX: ['\x1b[1;37m', '\x1b[1;34m'],
    Distributions.MANJARO_LINUX: ['\x1b[0;32m', '\x1b[1;32m'],
    Distributions.LINUX: ['\x1b[1;33m', '\x1b[1;37m'],
    Distributions.LINUX_MINT: ['\x1b[1;37m', '\x1b[1;32m'],
    Distributions.OPENSUSE: ['\x1b[1;37m', '\x1b[1;32m'],
    Distributions.RED_HAT: ['\x1b[1;37m', '\x1b[1;31m', '\x1b[0;31m'],
    Distributions.UBUNTU: ['\x1b[0;31m', '\x1b[1;31m', '\x1b[0;33m'],
    'sensors': ['\x1b[0;32m', '\x1b[0;33m', '\x1b[0;31m'],
    'clear': '\x1b[0m'
}

deDict = {
    'cinnamon': 'Cinnamon',
    'gnome-session': 'GNOME',
    'gnome-shell': 'GNOME',
    'mate-session': 'MATE',
    'ksmserver': 'KDE',
    'xfce4-session': 'Xfce',
    'fur-box-session': 'Fur Box',
    'lxsession': 'LXDE',
    'lxqt-session': 'LXQt'
}

wmDict = {
    'awesome': 'Awesome',
    'beryl': 'Beryl',
    'blackbox': 'Blackbox',
    'bspwm': 'bspwm',
    'cinnamon': 'Cinnamon',
    'compiz': 'Compiz',
    'dwm': 'DWM',
    'enlightenment': 'Enlightenment',
    'herbstluftwm': 'herbstluftwm',
    'fluxbox': 'Fluxbox',
    'fvwm': 'FVWM',
    'i3': 'i3',
    'icewm': 'IceWM',
    'kwin': 'KWin',
    'metacity': 'Metacity',
    'musca': 'Musca',
    'openbox': 'Openbox',
    'pekwm': 'PekWM',
    'qtile': 'QTile',
    'ratpoison': 'ratpoison',
    'scrotwm': 'ScrotWM',
    'stumpwm': 'StumpWM',
    'subtle': 'Subtle',
    'monsterwm': 'MonsterWM',
    'wingo': 'Wingo',
    'wmaker': 'Window Maker',
    'wmfs': 'Wmfs',
    'wmii': 'wmii',
    'xfwm4': 'Xfwm',
    'xmonad': 'xmonad'
}

logosDict = {
    Distributions.ARCH_LINUX: """
{c[1]}               +                 {r[0]}
{c[1]}               #                 {r[1]}
{c[1]}              ###                {r[2]}
{c[1]}             #####               {r[3]}
{c[1]}             ######              {r[4]}
{c[1]}            ; #####;             {r[5]}
{c[1]}           +##.#####             {r[6]}
{c[1]}          +##########            {r[7]}
{c[1]}         ######{c[0]}#####{c[1]}##;          {r[8]}
{c[1]}        ###{c[0]}############{c[1]}+         {r[9]}
{c[1]}       #{c[0]}######   #######{c[1]}         {r[10]}
{c[1]}     {c[0]}.######;     ;###;`\".{c[1]}       {r[11]}
{c[1]}    {c[0]}.#######;     ;#####.{c[1]}        {r[12]}
{c[1]}    {c[0]}#########.   .########`{c[1]}      {r[13]}
{c[1]}   {c[0]}######'           '######{c[1]}     {r[14]}
{c[1]}  {c[0]};####                 ####;{c[1]}    {r[15]}
{c[1]}  {c[0]}##'                     '##{c[1]}    {r[16]}
{c[1]} {c[0]}#'                         `#{c[1]}   {r[17]}\n""",
    Distributions.BUNSENLABS: """
{c[0]}           .{c[1]}..{c[0]}+hhy+-`         \0
{c[0]}        `+hd{c[1]}-{c[0]}+dddd{c[2]}hyso{c[0]}+//:    \0
{c[0]}      `+dddd{c[1]}:-{c[0]}sdh/.           {r[0]}
{c[0]}     -hdddddh{c[1]}-.{c[2]}/:{c[0]}             {r[1]}
{c[0]}    /ddddddddd{c[1]}:```{c[0]}            {r[2]}
{c[0]}   :ddddddddddd/              {r[3]}
{c[0]}  `hdddddddddddd+             {r[4]}
{c[0]}  /dddddddddddddd:            {r[5]}
{c[0]}  odddds..sddddddh            {r[6]}
{c[0]}  oddd/    /dddddd:           {r[7]}
{c[0]}  +dd+      +ddddd+           {r[8]}
{c[0]}  .dd`      `ddddd+           {r[9]}
{c[0]}   oh        ydddd:           {r[10]}
{c[0]}   `o        sdddh`           {r[11]}
{c[0]}             yddd:            {r[12]}
{c[0]}            `dddo             {r[13]}
{c[0]}     :s     :dds              {r[14]}
{c[0]}     yd/    yd+               {r[15]}
{c[0]}   `sddy   :h-                {r[16]}
{c[0]}  `sddys`  :`                 {r[17]}
{c[0]} -hdy+`y+yo./+/:-             \0
{c[0]} ...  .o++oso+/               \n""",
    Distributions.CRUNCHBANG: """
{c[0]}                 ___       ___      _    {r[0]}
{c[0]}                /  /      /  /     | |   {r[1]}
{c[0]}               /  /      /  /      | |   {r[2]}
{c[0]}              /  /      /  /       | |   {r[3]}
{c[0]}      _______/  /______/  /______  | |   {r[4]}
{c[0]}     /______   _______   _______/  | |   {r[5]}
{c[0]}           /  /      /  /          | |   {r[6]}
{c[0]}          /  /      /  /           | |   {r[7]}
{c[0]}         /  /      /  /            | |   {r[8]}
{c[0]}  ______/  /______/  /______       | |   {r[9]}
{c[0]} /_____   _______   _______/       | |   {r[10]}
{c[0]}      /  /      /  /               | |   {r[11]}
{c[0]}     /  /      /  /                |_|   {r[12]}
{c[0]}    /  /      /  /                  _    {r[13]}
{c[0]}   /  /      /  /                  | |   {r[14]}
{c[0]}  /__/      /__/                   |_|   {r[15]}
{c[0]}                                         {r[16]}
{c[0]}                                         {r[17]}\n""",
    Distributions.DEBIAN: """
{c[1]}                                  {r[0]}
{c[1]}          _sudZUZ#Z#XZo=_         {r[1]}
{c[1]}       _jmZZ2!!~---~!!X##wx       {r[2]}
{c[1]}    .<wdP~~            -!YZL,     {r[3]}
{c[1]}   .mX2'       _xaaa__     XZ[.   {r[4]}
{c[1]}   oZ[      _jdXY!~?S#wa   ]Xb;   {r[5]}
{c[1]}  _#e'     .]X2(     ~Xw|  )XXc   {r[6]}
{c[1]} .2Z`      ]X[.       xY|  ]oZ(   {r[7]}
{c[1]} .2#;      )3k;     _s!~   jXf`   {r[8]}
{c[1]}  {c[0]}1Z>{c[1]}      {c[0]}-]Xb/{c[1]}    {c[0]}~{c[1]}    {c[0]}__#2({c[1]}    {r[9]}
{c[1]}  {c[0]}-Zo;{c[1]}       {c[0]}+!4ZwerfgnZZXY'{c[1]}      {r[10]}
{c[1]}   {c[0]}*#[,{c[1]}        {c[0]}~-?!!!!!!-~{c[1]}        {r[11]}
{c[1]}    {c[0]}XUb;.{c[1]}                         {r[12]}
{c[1]}     {c[0]})YXL,,{c[1]}                       {r[13]}
{c[1]}       {c[0]}+3#bc,{c[1]}                     {r[14]}
{c[1]}         {c[0]}-)SSL,,{c[1]}                  {r[15]}
{c[1]}            {c[0]}~~~~~{c[1]}                 {r[16]}
{c[1]}                                  {r[17]}\n""",
    Distributions.FEDORA: """
{c[1]}           :/------------://          {r[0]}
{c[1]}        :------------------://        {r[1]}
{c[1]}      :-----------{c[0]}/shhdhyo/{c[1]}-://       {r[2]}
{c[1]}    /-----------{c[0]}omMMMNNNMMMd/{c[1]}-:/      {r[3]}
{c[1]}   :-----------{c[0]}sMMMdo:/{c[1]}       -:/     {r[4]}
{c[1]}  :-----------{c[0]}:MMMd{c[1]}-------    --:/    {r[5]}
{c[1]}  /-----------{c[0]}:MMMy{c[1]}-------    ---/    {r[6]}
{c[1]} :------    --{c[0]}/+MMMh/{c[1]}--        ---:   {r[7]}
{c[1]} :---     {c[0]}oNMMMMMMMMMNho{c[1]}     -----:   {r[8]}
{c[1]} :--      {c[0]}+shhhMMMmhhy++{c[1]}   ------:    {r[9]}
{c[1]} :-      -----{c[0]}:MMMy{c[1]}--------------/    {r[10]}
{c[1]} :-     ------{c[0]}/MMMy{c[1]}-------------:     {r[11]}
{c[1]} :-      ----{c[0]}/hMMM+{c[1]}------------:      {r[12]}
{c[1]} :--{c[0]}:dMMNdhhdNMMNo{c[1]}-----------:        {r[13]}
{c[1]} :---{c[0]}:sdNMMMMNds:{c[1]}----------:          {r[14]}
{c[1]} :------{c[0]}:://:{c[1]}-----------://           {r[15]}
{c[1]} :--------------------://             {r[16]}
{c[1]}                                      {r[17]}\n""",
    Distributions.GENTOO: """
{c[1]}          -/oyddmdhs+:.                {r[0]}
{c[1]}      -o{c[0]}dNMMMMMMMMNNmhy+{c[1]}-`             {r[1]}
{c[1]}    -y{c[0]}NMMMMMMMMMMMNNNmmdhy{c[1]}+-           {r[2]}
{c[1]}  `o{c[0]}mMMMMMMMMMMMMNmdmmmmddhhy{c[1]}/`        {r[3]}
{c[1]}  om{c[0]}MMMMMMMMMMMN{c[1]}hhyyyo{c[0]}hmdddhhhd{c[1]}o`      {r[4]}
{c[1]} .y{c[0]}dMMMMMMMMMMd{c[1]}hs++so/s{c[0]}mdddhhhhdm{c[1]}+`    {r[5]}
{c[1]}  oy{c[0]}hdmNMMMMMMMN{c[1]}dyooy{c[0]}dmddddhhhhyhN{c[1]}d.   {r[6]}
{c[1]}   :o{c[0]}yhhdNNMMMMMMMNNNmmdddhhhhhyym{c[1]}Mh   {r[7]}
{c[1]}     .:{c[0]}+sydNMMMMMNNNmmmdddhhhhhhmM{c[1]}my   {r[8]}
{c[1]}        /m{c[0]}MMMMMMNNNmmmdddhhhhhmMNh{c[1]}s:   {r[9]}
{c[1]}     `o{c[0]}NMMMMMMMNNNmmmddddhhdmMNhs{c[1]}+`    {r[10]}
{c[1]}   `s{c[0]}NMMMMMMMMNNNmmmdddddmNMmhs{c[1]}/.      {r[11]}
{c[1]}  /N{c[0]}MMMMMMMMNNNNmmmdddmNMNdso{c[1]}:`        {r[12]}
{c[1]} +M{c[0]}MMMMMMNNNNNmmmmdmNMNdso{c[1]}/-           {r[13]}
{c[1]} yM{c[0]}MNNNNNNNmmmmmNNMmhs+/{c[1]}-`             {r[14]}
{c[1]} /h{c[0]}MMNNNNNNNNMNdhs++/{c[1]}-`                {r[15]}
{c[1]} `/{c[0]}ohdmmddhys+++/:{c[1]}.`                   {r[16]}
{c[1]} `-//////:--.                          {r[17]}\n""",
    Distributions.KALI_LINUX: """
{c[0]}      ,.....                                        \0
{c[0]}  ----`     `..,;:ccc,.                             \0
{c[0]}           ......''';lxO.                           {r[0]}
{c[0]} .....''''..........,:ld;                           {r[1]}
{c[0]}            .';;;:::;,,.x,                          {r[2]}
{c[0]}       ..'''.            0Xxoc:,.  ...              {r[3]}
{c[0]}   ....                ,ONkc;,;cokOdc',.            {r[4]}
{c[0]}  .                   OMo           ':{c[1]}d{c[0]}o.           {r[5]}
{c[0]}                     dMc               :OO;         {r[6]}
{c[0]}                     0M.                 .:o.       {r[7]}
{c[0]}                     ;Wd                            {r[8]}
{c[0]}                      ;XO,                          {r[9]}
{c[0]}                        ,d0Odlc;,..                 {r[10]}
{c[0]}                            ..',;:cdOOd::,.         {r[11]}
{c[0]}                                     .:d;.':;.      {r[12]}
{c[0]}                                        'd,  .'     {r[13]}
{c[0]}                                          ;l   ..   {r[14]}
{c[0]}                                           .o       {r[15]}
{c[0]}                                             c      {r[16]}
{c[0]}                                             .'     {r[17]}
{c[0]}                                              .     \n""",
    Distributions.MANJARO_LINUX: """
{c[0]} $$$$$$$$$$$$$$$$  $$$$$$$   {r[0]}
{c[0]} M77777777777777M  M77777M   {r[1]}
{c[0]} M77777777777777M  M77777M   {r[2]}
{c[0]} M77777MMMMMMMMMM  M77777M   {r[3]}
{c[0]} M77777M           M77777M   {r[4]}
{c[0]} M77777M  $$$$$$$  M77777M   {r[5]}
{c[0]} MMMMMMM  M77777M  M77777M   {r[6]}
{c[0]}          M77777M  M77777M   {r[7]}
{c[0]} $$$$$$$  M77777M  M77777M   {r[8]}
{c[0]} M77777M  M77777M  M77777M   {r[9]}
{c[0]} M77777M  M77777M  M77777M   {r[10]}
{c[0]} M77777M  M77777M  M77777M   {r[11]}
{c[0]} M77777M  M77777M  M77777M   {r[12]}
{c[0]} M77777M  M77777M  M77777M   {r[13]}
{c[0]} M77777M  M77777M  M77777M   {r[14]}
{c[0]} M77777M  M77777M  M77777M   {r[15]}
{c[0]} M77777M  M77777M  M77777M   {r[16]}
{c[0]} MMMMMMM  MMMMMMM  MMMMMMM   {r[17]}\n""",
    Distributions.LINUX: """
{c[1]}                           {r[0]}
{c[1]}          a8888b.          {r[1]}
{c[1]}         d888888b.         {r[2]}
{c[1]}         8P"YP"Y88         {r[3]}
{c[1]}         8|o||o|88         {r[4]}
{c[1]}         8{c[0]}\\vvvv/{c[1]}88         {r[5]}
{c[1]}         8{c[0]} \\vv/ {c[1]}Y8.        {r[6]}
{c[1]}        d/  {c[0]}`'{c[1]}  \8b.       {r[7]}
{c[1]}      .dP   .     Y8b.     {r[8]}
{c[1]}     d8:'   "   `::88b.    {r[9]}
{c[1]}    d8"           `Y88b    {r[10]}
{c[1]}   :8P     '       :888    {r[11]}
{c[1]}    8a.    :      _a88P    {r[12]}
{c[1]}  {c[0]}._/"{c[1]}Yaa_ :    .{c[0]}| {c[1]}88P{c[0]}|{c[1]}    {r[13]}
{c[1]} {c[0]}\++++{c[1]}YP"      `{c[0]}| {c[1]}8P{c[0]}++\.{c[1]}   {r[14]}
{c[1]} {c[0]}/+++++\.{c[1]}_____.d{c[0]}|+++++/{c[1]}    {r[15]}
{c[1]}  {c[0]}\++++++){c[1]}888888P{c[0]}\+++/{c[1]}     {r[16]}
{c[1]}                           {r[17]}\n""",
    Distributions.LINUX_MINT: """
{c[1]}                                       {r[0]}
{c[1]} MMMMMMMMMMMMMMMMMMMMMMMMMmds+.        {r[1]}
{c[1]} MMm----::-://////////////oymNMd+`     {r[2]}
{c[1]} MMd      {c[0]}/++{c[1]}                -sNMd:    {r[3]}
{c[1]} MMNso/`  {c[0]}dMM{c[1]}    {c[0]}`.::-. .-::.`{c[1]} .hMN:   {r[4]}
{c[1]} ddddMMh  {c[0]}dMM{c[1]}   {c[0]}:hNMNMNhNMNMNh:`{c[1]} NMm   {r[5]}
{c[1]}     NMm  {c[0]}dMM{c[1]}  {c[0]}.NMN/-+MMM+-/NMN`{c[1]} dMM   {r[6]}
{c[1]}     NMm  {c[0]}dMM{c[1]}  {c[0]}-MMm{c[1]}  {c[0]}`MMM{c[1]}   {c[0]}dMM.{c[1]} dMM   {r[7]}
{c[1]}     NMm  {c[0]}dMM{c[1]}  {c[0]}-MMm{c[1]}  {c[0]}`MMM{c[1]}   {c[0]}dMM.{c[1]} dMM   {r[8]}
{c[1]}     NMm  {c[0]}dMM{c[1]}  {c[0]}.mmd{c[1]}  {c[0]}`mmm{c[1]}   {c[0]}yMM.{c[1]} dMM   {r[9]}
{c[1]}     NMm  {c[0]}dMM`{c[1]}  {c[0]}..`{c[1]}  {c[0]}`...{c[1]}   {c[0]}ydm.{c[1]} dMM   {r[10]}
{c[1]}     hMM-  {c[0]}+MMd/-------...-:sdds{c[1]} MMM   {r[11]}
{c[1]}     -NMm-  {c[0]}:hNMNNNmdddddddddy/`{c[1]} dMM   {r[12]}
{c[1]}      -dMNs-``{c[0]}-::::-------.``{c[1]}    dMM   {r[13]}
{c[1]}       `/dMNmy+/:-------------:/yMMM   {r[14]}
{c[1]}          ./ydNMMMMMMMMMMMMMMMMMMMMM   {r[15]}
{c[1]}                                       {r[16]}
{c[1]}                                       {r[17]}\n""",
    Distributions.OPENSUSE: """
{c[0]}            .;ldkO0000Okdl;.              {r[0]}
{c[0]}        .;d00xl:^''''''^:ok00d;.          {r[1]}
{c[0]}      .d00l'                'o00d.        {r[2]}
{c[0]}    .d0Kd'  {c[1]}Okxol:;,.{c[0]}          :O0d.      {r[3]}
{c[0]}   .OK{c[1]}KKK0kOKKKKKKKKKKOxo:,{c[0]}      lKO.     {r[4]}
{c[0]}  ,0K{c[1]}KKKKKKKKKKKKKKK0P^{c[0]},,,{c[1]}^dx:{c[0]}    ;00,    {r[5]}
{c[0]} .OK{c[1]}KKKKKKKKKKKKKKKk'{c[0]}.oOPPb.{c[1]}'0k.{c[0]}   cKO.   {r[6]}
{c[0]} :KK{c[1]}KKKKKKKKKKKKKKK: {c[0]}kKx..dd{c[1]} lKd{c[0]}   'OK:   {r[7]}
{c[0]} dKK{c[1]}KKKKKKKKKOx0KKKd {c[0]}^0KKKO'{c[1]} kKKc{c[0]}   dKd   {r[8]}
{c[0]} dKK{c[1]}KKKKKKKKKK;.;oOKx,..{c[0]}^{c[1]}..;kKKK0.{c[0]}  dKd   {r[9]}
{c[0]} :KK{c[1]}KKKKKKKKKK0o;...^cdxxOK0O/^^'{c[0]}  .0K:   {r[10]}
{c[0]}  kKK{c[1]}KKKKKKKKKKKKK0x;,,......,;od{c[0]}  lKk    {r[11]}
{c[0]}  '0K{c[1]}KKKKKKKKKKKKKKKKKKKK00KKOo^{c[0]}  c00'    {r[12]}
{c[0]}   'kK{c[1]}KKOxddxkOO00000Okxoc;''{c[0]}   .dKk'     {r[13]}
{c[0]}     l0Ko.                    .c00l'      {r[14]}
{c[0]}      'l0Kk:.              .;xK0l'        {r[15]}
{c[0]}         'lkK0xl:;,,,,;:ldO0kl'           {r[16]}
{c[0]}             '^:ldxkkkkxdl:^'             {r[17]}\n""",
    Distributions.RED_HAT: """
{c[1]}                                             {r[0]}
{c[1]}              {c[2]}\`.-..........\`{c[1]}               {r[1]}
{c[1]}             {c[2]}\`////////::.\`-/.{c[1]}              {r[2]}
{c[1]}             {c[2]}-: ....-////////.{c[1]}               {r[3]}
{c[1]}             {c[2]}//:-::///////////\`{c[1]}             {r[4]}
{c[1]}      {c[2]}\`--::: \`-://////////////:{c[1]}            {r[5]}
{c[1]}      {c[2]}//////-    \`\`.-://///////{c[1]} .\`        {r[6]}
{c[1]}      {c[2]}\`://////:-.\`    :///////::///:\`{c[1]}     {r[7]}
{c[1]}        {c[2]}.-/////////:---/////////////:{c[1]}        {r[8]}
{c[1]}           {c[2]}.-://////////////////////.{c[1]}        {r[9]}
{c[1]}          {c[0]}yMN+\`.-${c[2]}::///////////////-\`{c[1]}      {r[10]}
{c[1]}       {c[0]}.-\`:NMMNMs\`  \`..-------..\`{c[1]}        {r[11]}
{c[1]}        {c[0]}MN+/mMMMMMhoooyysshsss{c[1]}               {r[12]}
{c[1]} {c[0]}MMM    MMMMMMMMMMMMMMyyddMMM+{c[1]}               {r[13]}
{c[1]}  {c[0]}MMMM   MMMMMMMMMMMMMNdyNMMh\`     hyhMMM{c[1]}   {r[14]}
{c[1]}   {c[0]}MMMMMMMMMMMMMMMMyoNNNMMM+.   MMMMMMMM{c[1]}     {r[15]}
{c[1]}    {c[0]}MMNMMMNNMMMMMNM+ mhsMNyyyyMNMMMMsMM{c[1]}      {r[16]}
{c[1]}                                             {r[17]}\n""",
    Distributions.UBUNTU: """
{c[1]}                           {c[0]}.oyhhs:{c[1]}     {r[0]}
{c[1]}                  ..--.., {c[0]}shhhhhh-{c[1]}     {r[1]}
{c[1]}                -+++++++++`:{c[0]}yyhhyo`{c[1]}    {r[2]}
{c[1]}           {c[2]}.--{c[1]}  -++++++++/-.-{c[0]}::-`{c[1]}      {r[3]}
{c[1]}         {c[2]}.::::-{c[1]}   :-----:/+++/++/.     {r[4]}
{c[1]}        {c[2]}-:::::-.{c[1]}          .:++++++:    {r[5]}
{c[1]}   ,,, {c[2]}.:::::-`{c[1]}             .++++++-   {r[6]}
{c[1]} ./+++/-{c[2]}`-::-{c[1]}                ./////:   {r[7]}
{c[1]} +++++++ {c[2]}.::-{c[1]}                          {r[8]}
{c[1]} ./+++/-`{c[2]}-::-{c[1]}                {c[0]}:yyyyyo{c[1]}   {r[9]}
{c[1]}   ``` `{c[2]}-::::-`{c[1]}             {c[0]}:yhhhhh:{c[1]}   {r[10]}
{c[1]}       {c[2]}-:::::-.{c[1]}         {c[0]}`-ohhhhhh+{c[1]}    {r[11]}
{c[1]}         {c[2]}.::::-`{c[1]} {c[0]}-o+///+oyhhyyyhy:{c[1]}     {r[12]}
{c[1]}          {c[2]}`.--{c[1]}  {c[0]}/yhhhhhhhy+{c[2]},....{c[1]}       {r[13]}
{c[1]}                {c[0]}/hhhhhhhhh{c[2]}-.-:::;{c[1]}      {r[14]}
{c[1]}                {c[0]}`.:://::- {c[2]}-:::::;{c[1]}      {r[15]}
{c[1]}                          {c[2]}`.-:-'{c[1]}       {r[16]}
{c[1]}                                       {r[17]}\n"""
}


# ---------- Global variables --------- #

# We'll list the running processes only one time
PROCESSES = check_output([
                          'ps',
                          '-u' + str(getuid()) if getuid() != 0 else '-ax',
                          '-o', 'comm', '--no-headers'
                        ]).decode().rstrip().split('\n')

# Default strings for non-reachable information
NO_ADRESS = 'No Address '
NOT_DETECTED = 'Not detected'


# -------------- Classes -------------- #

class Output:
    def __init__(self):
        self.results = []
        lsbOutput = check_output(['lsb_release', '-i', '-s']).decode().rstrip()

        for distribution in Distributions:
            if re.fullmatch(distribution.value, lsbOutput):
                self.distribution = distribution
                break

        else:
            self.distribution = Distributions.LINUX

    def append(self, key, value):
        self.results.append('{0}{1}:{2} {3}'.format(
            colorDict[self.distribution][1], key, colorDict['clear'], value))

    def output(self):
        results = []
        results.extend([''] * floor((18 - len(self.results)) / 2))
        results.extend(self.results[:])

        if len(results) < 18:
            results.extend([''] * (18 - len(results)))

        print(logosDict[self.distribution].format(
            c=colorDict[self.distribution], r=results) + colorDict['clear'])


class User:
    def __init__(self):
        self.value = getenv('USER', NOT_DETECTED)


class Hostname:
    def __init__(self):
        self.value = check_output(['uname', '-n']).decode().rstrip()


class Model:
    def __init__(self):
        try:
            with open('/sys/devices/virtual/dmi/id/product_name') as file:
                model = file.read().rstrip()

        except FileNotFoundError:
            # The file above does not exist, is this device a Raspberry Pi ?
            # Let's retrieve the Hardware and Revision IDs with `/proc/cpuinfo`
            with open('/proc/cpuinfo') as file:
                output = file.read()
                hardware = re.search('(?<=Hardware\t: ).*', output)
                revision = re.search('(?<=Revision\t: ).*', output)

            # If the output contains 'Hardware' and 'Revision'...
            if hardware and revision:
                # ... let's set a pretty info string with these data
                model = 'Raspberry Pi ' + hardware.group(0) + \
                        ' (Rev. ' + revision.group(0) + ')'

            else:
                # A tricky way to retrieve some details about hypervisor...
                # ... within virtualized contexts.
                # `archey` needs to be run as root although.
                try:
                    virtWhat = ', '.join(check_output([
                                                       'virt-what'
                                                      ],
                                                      stderr=DEVNULL)
                                         .decode().rstrip().split())

                    if virtWhat:
                        try:
                            # Sometimes we may gather info added by...
                            # ... hosting service provider this way
                            model = check_output([
                                                  'dmidecode',
                                                  '-s',
                                                  'system-product-name'
                                                 ], stderr=DEVNULL
                                                 ).decode().rstrip()

                        except (FileNotFoundError, CalledProcessError):
                            model = 'Virtualized environment'

                        model += ' (' + virtWhat + ')'

                    else:
                        model = 'Bare-metal environment'

                except (FileNotFoundError, CalledProcessError):
                    model = NOT_DETECTED

        self.value = model


class Distro:
    def __init__(self):
        self.value = check_output(['lsb_release', '-d', '-s']
                                  ).decode().rstrip() + \
                     ' ' + check_output(['uname', '-m']).decode().rstrip()


class Kernel:
    def __init__(self):
        self.value = check_output(['uname', '-r']).decode().rstrip()


class Uptime:
    def __init__(self):
        with open('/proc/uptime') as file:
            fuptime = int(file.read().split('.')[0])

        day, fuptime = divmod(fuptime, 86400)
        hour, fuptime = divmod(fuptime, 3600)
        minute = fuptime // 60

        uptime = ''
        uptime += ((str(day) + ' day' + ('s' if day > 1 else '') + ('' if minute == 0 and hour == 0 else (' and ' if (minute != 0 and hour == 0) or (minute == 0 and hour != 0) else ', '))) if day >= 1 else '')
        uptime += ((str(hour) + ' hour' + ('s' if hour > 1 else '') + (' and ' if minute != 0 else '')) if hour >= 1 else '')
        uptime += ((str(minute) + ' minute' + ('s' if minute > 1 else '')) if minute >= 1 else ('< 1 minute' if day == 0 and hour == 0 else ''))

        self.value = uptime


class WindowManager:
    def __init__(self):
        try:
            wm = re.search('(?<=Name: ).*',
                           check_output(['wmctrl', '-m'],
                                        stderr=DEVNULL).decode()).group(0)

        except (FileNotFoundError, CalledProcessError):
            for key in wmDict.keys():
                if key in PROCESSES:
                    wm = wmDict[key]
                    break

            else:
                wm = NOT_DETECTED

        self.value = wm


class DesktopEnvironment:
    def __init__(self):
        for key in deDict.keys():
            if key in PROCESSES:
                de = deDict[key]
                break

        else:
            # Let's rely on an environment var if the loop above didn't `break`
            de = getenv('XDG_CURRENT_DESKTOP', NOT_DETECTED)

        self.value = de


class Shell:
    def __init__(self):
        self.value = getenv('SHELL', NOT_DETECTED)


class Terminal:
    def __init__(self):
        self.value = getenv('TERM', NOT_DETECTED)


class Packages:
    def __init__(self):
        for packagesTool in [
                                ['pacman', '-Q'],
                                ['dnf', 'list', 'installed'],
                                ['dpkg', '--get-selections'],
                                ['zypper', 'search', '--installed-only'],
                                ['emerge', '-ep', 'world'],
                                ['rpm', '-qa']
                            ]:
            try:
                results = check_output(packagesTool, stderr=DEVNULL).decode()
                packages = len(results.rstrip().split('\n'))

                if 'dpkg' in packagesTool:
                    packages -= results.count('deinstall')

                break

            except (FileNotFoundError, CalledProcessError):
                packages = NOT_DETECTED

        self.value = packages


class CPU:
    def __init__(self):
        with open('/proc/cpuinfo') as file:
            self.value = re.search('(?<=model name\t: ).*',
                                   file.read()).group(0)


class GPU:
    def __init__(self):
        try:
            gpuinfo = check_output(['grep', '-E', '3D|VGA|Display'],
                                   stdin=Popen(['lspci'],
                                   stdout=PIPE, stderr=DEVNULL).stdout
                                   ).decode().split(': ')[1].rstrip()

            # If the line got too long, let's truncate it and add some dots...
            if len(gpuinfo) > 48:
                gpuinfo = re.findall('.{1,45}(?:\W|$)',
                                     gpuinfo)[0].strip() + '...'

        except (FileNotFoundError, CalledProcessError):
            gpuinfo = NOT_DETECTED

        self.value = gpuinfo


class RAM:
    def __init__(self):
        try:
            ram = ''.join(filter(re.compile('M').search,
                          Popen(['free', '-m'], stdout=PIPE, env={'LANG': 'C'}
                                ).communicate()[0].decode().split('\n'))
                          ).split()
            used = float(ram[2])
            total = float(ram[1])

        except IndexError:
            with open('/proc/meminfo') as file:
                ram = file.read().split('\n')

            # A little closure to convert `/proc/meminfo` lines as `float`
            def convert(line):
                return float(line.split(':')[1].strip(' kB'))

            total = convert(ram[0]) / 1024
            used = total - ((convert(ram[1]) + convert(ram[3]) +
                             convert(ram[4]) + convert(ram[22])) / 1024)

        self.value = '{0}{1} MB{2} / {3} MB'.format(
                        colorDict['sensors'][int((used / total) * 100) // 33],
                        int(used), colorDict['clear'], int(total))


class Disk:
    def __init__(self):
        total = re.sub(',', '.', check_output(['df', '-Tlh', '-B', 'GB', '--total', '-t', 'ext4', '-t', 'ext3', '-t', 'ext2', '-t', 'reiserfs', '-t', 'jfs', '-t', 'ntfs', '-t', 'fat32', '-t', 'btrfs', '-t', 'fuseblk', '-t', 'xfs', '-t', 'simfs', '-t', 'tmpfs', '-t', 'zfs']).decode().splitlines()[-1]).split()

        self.value = '{0}{1}{2} / {3}'.format(
                        colorDict['sensors'][int(total[5][:-1]) // 33],
                        re.sub('GB', ' GB', total[3]), colorDict['clear'],
                        re.sub('GB', ' GB', total[2]))


class LAN_IP:
    def __init__(self):
        try:
            self.value = ', '.join(check_output(['hostname', '-I'],
                                                stderr=DEVNULL
                                                ).decode().rstrip().split()
                                   ) or NO_ADRESS

        except CalledProcessError:
            # Slow manual workaround for old `inetutils` versions, with `ip`
            self.value = ', '.join(check_output(['cut', '-d', ' ', '-f', '3'], stdin=Popen(['cut', '-d', '/', '-f', '1'], stdout=PIPE, stdin=Popen(['tr', '-s', ' '], stdout=PIPE, stdin=Popen(['grep', '-v', ' lo'], stdout=PIPE, stdin=Popen(['grep', 'inet '], stdout=PIPE, stdin=Popen(['ip', 'addr', 'show', 'up'], stdout=PIPE).stdout).stdout).stdout).stdout).stdout).decode().split()) or NO_ADRESS


class WAN_IP:
    def __init__(self):
        try:
            try:
                self.value = check_output([
                                           'dig', '+short', 'myip.opendns.com',
                                           '@resolver1.opendns.com'
                                          ], timeout=1, stderr=DEVNULL
                                          ).decode().rstrip()

            except FileNotFoundError:
                self.value = check_output([
                                           'wget', '-qO-', 'https://ident.me/'
                                           ], timeout=1).decode()

        except (CalledProcessError, TimeoutExpired):
            self.value = NO_ADRESS


# -------------- Classes' Enumeration -------------- #

class Classes(Enum):
    User = User
    Hostname = Hostname
    Model = Model
    Distro = Distro
    Kernel = Kernel
    Uptime = Uptime
    WindowManager = WindowManager
    DesktopEnvironment = DesktopEnvironment
    Shell = Shell
    Terminal = Terminal
    Packages = Packages
    CPU = CPU
    GPU = GPU
    RAM = RAM
    Disk = Disk
    LAN_IP = LAN_IP
    WAN_IP = WAN_IP


# -------------- Main -------------- #

if __name__ == '__main__':

    output = Output()
    for key in Classes:
        output.append(key.name, key.value().value)
    output.output()
