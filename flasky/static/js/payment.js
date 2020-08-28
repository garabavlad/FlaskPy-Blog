const chckout_btn = document.querySelector('#checkout-button');

if (chckout_btn)
    chckout_btn.addEventListener("click", event => {
        fetch('/checkout_session', {method: 'POST'})
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                const stripe = Stripe(data.pk);
                return stripe.redirectToCheckout({sessionId: data.id});
            })
            .then(function (result) {
                // If `redirectToCheckout` fails due to a browser or network
                // error, you should display the localized error message to your
                // customer using `error.message`.
                if (result.error) {
                    alert(result.error.message);
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
            });
    });


