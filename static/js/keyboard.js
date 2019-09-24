$(function()
{
	var write = document.getElementById("anbul").value
	shift = false,
	capslock = false;

	$('#keyboard li').click(function()
	{
		var $this = $(this),
			character = $this.html(); // If it's a lowercase letter, nothing happens to this variable

		// Special characters
		if ($this.hasClass('symbol')) character = "";
		if ($this.hasClass('space')) character = "";
		if ($this.hasClass('tab')) character = "";
		if ($this.hasClass('return')) character = "";

    // Delete
    if ($this.hasClass('delete')) {
      write = write.substring(0, write.length - 1)
    }
    // Add the character
    else
    {
      write = write + character;
    }
    document.getElementById("anbul").value = write;
	});
});
