// DO the forget password and forget username in login page...
// Add front page and changes in home pages..                       done //
// Add content in about us page..
// Add footer in all pages with copyrights..

//In expenses add table for the showing history of expenses  and add remaining budget on top
//In budget add table for the showing history of budget and add remaining budget
//In savings model add monthly or daily savings and add table for the showing history of savings

//******And add the searching and history from current month in all models in stat module*****
//that shows all savings and expenses and over a month




   // const button = document.getElementById("aboutus");
   //
   //  button.addEventListener('click',function ()
   //  {
   //      alert("This Page is in Construction");
   //  });

document.addEventListener('DOMContentLoaded', function() {
        const tableBody = document.getElementById('expenseTableBody');
        const viewMoreBtn = document.getElementById('viewMoreBtn');
        const viewLessBtn = document.getElementById('viewLessBtn');
        const hiddenRows = tableBody ? tableBody.querySelectorAll('.hidden-row') : [];
        const initialVisibleCount = 5;

        if (viewMoreBtn) {
            viewMoreBtn.addEventListener('click', function() {
                hiddenRows.forEach(row => {
                    row.style.display = 'table-row';
                });
                viewMoreBtn.style.display = 'none';
                viewLessBtn.style.display = 'inline-block';
            });
        }

        if (viewLessBtn) {
            viewLessBtn.addEventListener('click', function() {
                hiddenRows.forEach((row, index) => {
                    if (index >= initialVisibleCount - 5) {
                        row.style.display = 'none';
                    }
                });
                viewMoreBtn.style.display = 'inline-block';
                viewLessBtn.style.display = 'none';
            });
        }
    });