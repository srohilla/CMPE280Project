/* globals hopscotch: false */

/* ============ */
/* EXAMPLE TOUR */
/* ============ */


 // Define the tour!
    var tour = {
      id: "garvis",
      steps: [
        {
          title: "My Header",
          content: "This is the header of my page.",
          target: "garvis",
          placement: "bottom"
        },
        {
          title: "My content",
          content: "Here is where I put my content.",
          target: "head3",
          placement: "bottom"
        }
      ],
       onStart: function() {
        $('head1').addClass('selected');
      }
    };

    // Start the tour!
    hopscotch.startTour(tour);
