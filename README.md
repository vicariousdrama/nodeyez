# About Nodeyez

Nodeyez is a project that contains a variety of python [scripts](./scripts) to
produce images based on your Bitcoin Node

Images can be displayed to video output such as an attached screen on a
Raspberry Pi, as well as to a website dashboard for browser based access. In
addition, some scripts have support for reporting data to a local
[Blockclock Mini](https://blockclockmini.com/).

Scripts can be run on their own, or run continuously in the background as a service on system startup.

## Sample Panels Created by Nodeyez
<!-- sliders from blog.logrocket.com/build-image-carousel-from-scratch-vanilla-javascript/  -->
<script>
  function setupSliders() {
    const slides = document.querySelectorAll(".slide");
    slides.forEach((slide, indx) => { slide.style.transform = `translateX(${indx * 100}%)`; });
    let curSlide = 0;
    let maxSlide = slides.length - 1;
    const nextSlide = document.querySelector(".btn-next");
    nextSlide.addEventListener("click", function() {
      if(curSlide === maxSlide) {curSlide=0;} else {curSlide++;};
      slides.forEach((slide, indx) => {
        slide.style.transform = `translateX(${100 * (indx - curSlide)}%)`;
      });
    });
    const prevSlide = document.querySelector(".btn-prev");
    prevSlide.addEventListener("click", function() {
      if(curSlide === 0) {curSlide=maxSlide;} else {curSlide--;};
      slides.forEach((slide, indx) => {
        slide.style.transform = `translateX(${100 * (indx - curSlide)}%)`;
      });
    });
    var sliderstyle = document.createElement('style');
    sliderstyle.innerHTML = `
    .slider { width: 100%; max-with: 600px; height: 400px; position: relative; overflow: hidden; border-radius: 15px; }
    .slide { width: 100%; max-width: 600px; height: 400px; position: absolute; transition: all 0.5s; }
    .slide img { width: 100%; height: 100%; object-fit: cover; }
    .btn { position: absolute; width: 40px; height: 40px; padding: 10px; border: none; border-radius: 50%; z-index: 10px; cursor: pointer; background-color: #fff; font-size: 18px; }
    .btn:active { transform: scale(1.1); }
    .btn-prev { top: 45%; left: 2%; }
    .btn-next { top: 45%; right: 2%; }
    `;
    document.head.appendChild(sliderstyle);
  }
  window.addEventListener('load', setupSliders);
</script>
<div class="slider">
  <div class="slide"><img src="./images/arthash-719360.png" width=196 /></div>
  <div class="slide"><img src="./images/arthashdungeon.png" width=196 /></div>
  <div class="slide"><img src="./images/blockheight.png" width=196 /></div>
  <div class="slide"><img src="./images/channelbalance.png" width=196 /></div>
  <div class="slide"><img src="./images/channelfees.png" width=196 /></div>
  <div class="slide"><img src="./images/compassminingstatus.png" width=196 /></div>
  <div class="slide"><img src="./images/difficultyepoch.png" width=196 /></div>
  <div class="slide"><img src="./images/f2pool.png" width=196 /></div>
  <div class="slide"><img src="./images/fearandgreed.png" width=196 /></div>
  <div class="slide"><img src="./images/fiatprice.png" width=196 /></div>
  <div class="slide"><img src="./images/inscriptionmempool.png" width=196 /></div>
  <div class="slide"><img src="./images/ipaddress.png" width=196 /></div>
  <div class="slide"><img src="./images/lndhub.png" width=196 /></div>
  <div class="slide"><img src="./images/logo.png" width=196 /></div>
  <div class="slide"><img src="./images/luxor-mining-hashrate-2021-12.png" width=196 /></div>
  <div class="slide"><img src="./images/mempoolblocks.png" width=196 /></div>
  <div class="slide"><img src="./images/minerbraiins.png" width=196 /></div>
  <div class="slide"><img src="./images/opreturn.png" width=196 /></div>
  <div class="slide"><img src="./images/ordinals.png" width=196 /></div>
  <div class="slide"><img src="./images/rof-sample.png" width=196 /></div>
  <div class="slide"><img src="./images/satsperusd.png" width=196 /></div>
  <div class="slide"><img src="./images/slushpool.png" width=196 /></div>
  <div class="slide"><img src="./images/sysinfo.png" width=196 /></div>
  <div class="slide"><img src="./images/utcclock.png" width=196 /></div>
  <div class="slide"><img src="./images/whirlpoolclimix.png" width=196 /></div>
  <div class="slide"><img src="./images/whirlpoolliquidity.png" width=196 /></div>
  <button class="btn btn-next">&gt;</button>
  <button class="btn btn-prev">&lt;</button>
</div>

## Informational Panels

* [IP Address](./_docs/script-ipaddress.md)
* [System Metrics](./_docs/script-sysinfo.md)
* [UTC Clock](./_docs/script-utcclock.md)

## Bitcoin Panels

All of these panels can work with a local Bitcoin node. At this time, information is accessed via bitcoin-cli RPC calls.

* [Art Hash](./_docs/script-arthash.md)
* [Blockhash Dungeon](./_docs/script-arthashdungeon.md)
* [Block Height](./_docs/script-blockheight.md)
* [Difficulty Epoch](./_docs/script-difficultyepoch.md)
* [Halving Countdown](./_docs/script-halving.md)
* [Inscription Mempool](./_docs/script-inscriptionmempool.md)
* [Mempool Blocks](./_docs/script-mempoolblocks.md)
* [OP_RETURN](./_docs/script-opreturn.md)
* [Ordinal Inscriptions](./_docs/script-ordinals.md)

## Lighting (LND) Panels

These panels can be configured to report on local LND based nodes, as well as remote ones over REST.

* [Channel Balance](./_docs/script-channelbalance.md)
* [Channel Fees](./_docs/script-channelfees.md)
* [LND Hub Account Balances](./_docs/script-lndhub.md)
* [Ring of Fire](./_docs/script-rofstatus.md)

## Mining Panels

* [F2 Pool](./_docs/script-f2pool.md)
* [Luxor Pool](./_docs/script-luxor-mining-hashrate.md)
* [Miner - Braiins](./_docs/script-minerbraiins.md)
* [Miner - MicroBT](./_docs/script-minermicrobt.md)
* [Braiins Pool](./_docs/script-slushpool.md)

## Other Fun Panels

* [Dual Image Display](./_docs/script-nodeyezdual.md)
* [Fear and Greed Index](./_docs/script-fearandgreed.md)
* [Price of Bitcoin](./_docs/script-fiatprice.md)
* [Sats per USD](./_docs/script-satsperusd.md)
* [Whirlpool CLI Mix Status](./_docs/script-whirlpoolclimix.md)
* [Whirlpool Liquidity](./_docs/script-whirlpoolliquidity.md)

## No Longer Supported

The scripts are still available, but may not properly function as the data providers have changed from open standards or charge exhorbitant fees.

* [Compass Mining Hardware](./_docs/script-compassmininghardware.md)
* [Compass Mining Status](./_docs/script-compassminingstatus.md)
* [Gas Price](./_docs/script-gasprice.md)
* [Raretoshi](./_docs/script-raretoshi.md)

# Installation Procedures

1. [Raspberry Pi](./_install_steps/install-1-raspberrypinode.md)
2. [Python and Dependencies](./_install_steps/install-2-pythondeps.md)
3. [Display Screen](./_install_steps/install-3-displayscreen.md)
4. [Nodeyez User](./_install_steps/install-4-nodeyez.md)
5. [Website Dashboard](./_install_steps/install-5-websitedashboard.md)
6. [Running at Startup](./_install_steps/install-6-runatstartup.md)


