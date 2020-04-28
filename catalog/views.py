from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin 
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime
from .form import RenewBookForm
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    # The 'all()' is implied by default.    
    num_authors = Author.objects.count()
    
    num_genre = Genre.objects.count()	

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre' : num_genre,
        'num_visits' : num_visits
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'   # your own name for the list as a template variable
    template_name = 'book_list.html'  # Specify your own template name/location
    paginate_by = 5
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
    	context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
    	context['some_data'] = 'This is just some data'
    	return context

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'   # your own name for the list as a template variable
    template_name = 'author_list.html'  # Specify your own template name/location
    paginate_by = 5
    

class AuthorDetailView(generic.DetailView):
    model = Author
    paginate_by=2
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(author_id=kwargs['object'].id)
        return context
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 5
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
class LoanedBooksListView(PermissionRequiredMixin,generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed.html'
    paginate_by = 5
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')   


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


class AuthorCreate(PermissionRequiredMixin,CreateView):
	permission_required = 'catalog.can_modify_author'
	model = Author
	fields = '__all__'
	initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
	permission_required = 'catalog.can_modify_author'
	model = Author
	fields = ['first_name','last_name','date_of_birth','date_of_death']


class AuthorDelete(PermissionRequiredMixin,DeleteView):
	permission_required = 'catalog.can_modify_author'
	model = Author
	success_url = reverse_lazy('authors')    

class BookCreate(PermissionRequiredMixin,CreateView):
	permission_required = 'catalog.can_modify_book'
	model = Book
	fields = '__all__'

class BookUpdate(PermissionRequiredMixin,UpdateView):
	permission_required = 'catalog.can_modify_book'
	model = Book
	fields = '__all__'


class BookDelete(PermissionRequiredMixin,DeleteView):
	permission_required = 'catalog.can_modify_book'
	model = Book
	success_url = reverse_lazy('books')    	